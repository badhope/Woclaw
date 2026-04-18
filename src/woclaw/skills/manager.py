"""
Woclaw Skill Manager - 技能管理器
支持从 ai-skill 仓库和 GitHub 一键安装技能
"""

import os
import json
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


SKILL_REGISTRY_URL = "https://raw.githubusercontent.com/badhope/ai-skill/main/registry.json"
SKILL_REPO_URL = "https://github.com/badhope/ai-skill"
SKILLS_DIR = Path.home() / ".woclaw" / "skills"


@dataclass
class SkillInfo:
    """技能信息"""
    name: str
    version: str
    description: str
    description_en: str = ""
    author: str = ""
    category: str = "general"
    tags: list = field(default_factory=list)
    requires: list = field(default_factory=list)
    entry: str = "scripts/run.py"
    installed: bool = False
    path: str = ""


class SkillManager:
    """
    技能管理器
    支持：
    - 从官方仓库安装
    - 从 GitHub 直接安装
    - 本地技能管理
    - 技能搜索
    - 🧬 AI 自主进化技能
    """

    def __init__(self):
        self.skills_dir = SKILLS_DIR
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._registry: dict = {}
        self._installed: dict = {}
        self._evolution_engine = None
        self._load_installed()

    def get_evolution_engine(self, llm=None):
        """获取进化引擎实例"""
        if self._evolution_engine is None:
            try:
                import sys
                evolution_path = Path(__file__).parent / "evolution" / "modules"
                sys.path.insert(0, str(evolution_path))
                from evolution_engine import EvolutionEngine

                evolution_config_path = Path(__file__).parent / "evolution" / "config.json"
                config = {}
                if evolution_config_path.exists():
                    import json
                    with open(evolution_config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)

                self._evolution_engine = EvolutionEngine(
                    skill_path=Path(__file__).parent / "evolution",
                    config=config,
                    llm=llm,
                    skill_manager=self
                )
            except Exception as e:
                print(f"⚠️  进化引擎初始化失败: {e}")
        return self._evolution_engine

    async def evolve(self, task: str, llm=None) -> dict:
        """触发技能进化"""
        engine = self.get_evolution_engine(llm=llm)
        if engine is None:
            return {"success": False, "error": "进化引擎不可用"}

        return await engine.start_evolution_cycle(task)

    async def evolution_status(self) -> dict:
        """获取进化状态"""
        engine = self.get_evolution_engine()
        if engine is None:
            return {"success": False, "error": "进化引擎不可用"}
        return await engine.get_status()

    async def list_evolved_skills(self) -> dict:
        """列出进化生成的技能"""
        engine = self.get_evolution_engine()
        if engine is None:
            return {"success": False, "error": "进化引擎不可用"}
        return await engine.list_evolved_skills()

    def _load_installed(self):
        """加载已安装的技能"""
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                config_file = skill_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        self._installed[config.get("name", skill_dir.name)] = {
                            "path": str(skill_dir),
                            "config": config
                        }
                    except Exception:
                        pass

    async def fetch_registry(self) -> dict:
        """获取技能注册表"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(SKILL_REGISTRY_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        self._registry = await resp.json()
                        return self._registry
        except Exception:
            pass
        return {}

    async def search(self, keyword: str = "") -> list[SkillInfo]:
        """搜索技能"""
        await self.fetch_registry()

        results = []
        skills = self._registry.get("skills", [])

        for skill in skills:
            name = skill.get("name", "")
            desc = skill.get("description", "")
            tags = skill.get("tags", [])

            if not keyword or (
                keyword.lower() in name.lower() or
                keyword.lower() in desc.lower() or
                any(keyword.lower() in t.lower() for t in tags)
            ):
                info = SkillInfo(
                    name=name,
                    version=skill.get("version", "1.0.0"),
                    description=desc,
                    description_en=skill.get("description_en", ""),
                    author=skill.get("author", ""),
                    category=skill.get("category", "general"),
                    tags=tags,
                    requires=skill.get("requires", []),
                    installed=name in self._installed
                )
                results.append(info)

        return results

    async def install(self, skill_name: str, source: str = None) -> dict:
        """
        安装技能

        Args:
            skill_name: 技能名称，支持以下格式：
                - file-organizer (从官方仓库)
                - badhope/ai-skill/file-organizer (从 GitHub)
                - https://github.com/user/repo (整个仓库)
            source: 可选的来源 URL

        Returns:
            安装结果
        """
        print(f"✨ 正在安装技能: {skill_name}")

        # 解析来源
        if "/" in skill_name and not skill_name.startswith("http"):
            # GitHub 格式: user/repo/skill
            parts = skill_name.split("/")
            if len(parts) >= 3:
                user, repo, skill = parts[0], parts[1], "/".join(parts[2:])
                github_url = f"https://github.com/{user}/{repo}"
                return await self._install_from_github(github_url, skill)
            elif len(parts) == 2:
                # user/repo 格式
                github_url = f"https://github.com/{parts[0]}/{parts[1]}"
                return await self._install_from_github(github_url)
        elif skill_name.startswith("http"):
            return await self._install_from_github(skill_name)
        else:
            # 从官方仓库安装
            return await self._install_from_registry(skill_name)

    async def _install_from_registry(self, skill_name: str) -> dict:
        """从官方仓库安装"""
        # 构建下载 URL
        skill_url = f"https://github.com/badhope/ai-skill/tree/main/skills/{skill_name}"
        raw_base = f"https://raw.githubusercontent.com/badhope/ai-skill/main/skills/{skill_name}"

        # 下载 config.json
        config = await self._fetch_json(f"{raw_base}/config.json")
        if not config:
            return {"success": False, "error": f"技能不存在: {skill_name}"}

        # 创建技能目录
        skill_dir = self.skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # 下载文件
        files_to_download = [
            "config.json",
            "SKILL.md",
            "scripts/run.py",
            "requirements.txt",
        ]

        downloaded = []
        for file_path in files_to_download:
            url = f"{raw_base}/{file_path}"
            local_path = skill_dir / file_path
            local_path.parent.mkdir(parents=True, exist_ok=True)

            content = await self._fetch_text(url)
            if content:
                local_path.write_text(content, encoding='utf-8')
                downloaded.append(file_path)

        if not downloaded:
            return {"success": False, "error": "下载失败"}

        # 安装依赖
        if config.get("requires"):
            await self._install_requirements(config["requires"])

        # 更新已安装列表
        self._installed[skill_name] = {
            "path": str(skill_dir),
            "config": config
        }

        print(f"✅ 技能安装成功: {skill_name}")
        return {"success": True, "skill": skill_name, "path": str(skill_dir)}

    async def _install_from_github(self, repo_url: str, skill_path: str = None) -> dict:
        """从 GitHub 安装"""
        print(f"  从 GitHub 安装: {repo_url}")

        # 使用 git clone
        temp_dir = self.skills_dir / "_temp_install"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(temp_dir)],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                return {"success": False, "error": f"克隆失败: {result.stderr}"}

            if skill_path:
                # 安装特定技能
                source_dir = temp_dir / "skills" / skill_path
                if not source_dir.exists():
                    source_dir = temp_dir / skill_path

                if source_dir.exists():
                    skill_name = source_dir.name
                    target_dir = self.skills_dir / skill_name

                    if target_dir.exists():
                        shutil.rmtree(target_dir)

                    shutil.copytree(str(source_dir), str(target_dir))

                    # 加载配置
                    config_file = target_dir / "config.json"
                    if config_file.exists():
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        self._installed[skill_name] = {
                            "path": str(target_dir),
                            "config": config
                        }

                    print(f"✅ 技能安装成功: {skill_name}")
                    return {"success": True, "skill": skill_name}
                else:
                    return {"success": False, "error": f"技能目录不存在: {skill_path}"}
            else:
                # 安装仓库中所有技能
                skills_dir = temp_dir / "skills"
                if skills_dir.exists():
                    installed = []
                    for skill_dir in skills_dir.iterdir():
                        if skill_dir.is_dir():
                            target = self.skills_dir / skill_dir.name
                            if target.exists():
                                shutil.rmtree(target)
                            shutil.copytree(str(skill_dir), str(target))
                            installed.append(skill_dir.name)

                    print(f"✅ 安装了 {len(installed)} 个技能: {', '.join(installed)}")
                    return {"success": True, "skills": installed}
                else:
                    return {"success": False, "error": "仓库中没有 skills 目录"}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "克隆超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    async def _install_requirements(self, requirements: list):
        """安装 Python 依赖"""
        if not requirements:
            return

        print(f"  安装依赖: {', '.join(requirements)}")
        try:
            subprocess.run(
                ["pip", "install"] + requirements,
                capture_output=True, timeout=120
            )
        except Exception as e:
            print(f"  ⚠️ 依赖安装失败: {e}")

    async def _fetch_json(self, url: str) -> Optional[dict]:
        """获取 JSON"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json(content_type=None)
        except Exception:
            pass
        return None

    async def _fetch_text(self, url: str) -> Optional[str]:
        """获取文本"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.text()
        except Exception:
            pass
        return None

    def list_installed(self) -> list[SkillInfo]:
        """列出已安装的技能"""
        result = []
        for name, info in self._installed.items():
            config = info.get("config", {})
            result.append(SkillInfo(
                name=name,
                version=config.get("version", "1.0.0"),
                description=config.get("description", ""),
                description_en=config.get("description_en", ""),
                author=config.get("author", ""),
                category=config.get("category", "general"),
                tags=config.get("tags", []),
                installed=True,
                path=info.get("path", "")
            ))
        return result

    async def run(self, skill_name: str, args: list = None) -> dict:
        """运行技能"""
        if skill_name not in self._installed:
            return {"success": False, "error": f"技能未安装: {skill_name}"}

        skill_info = self._installed[skill_name]
        skill_path = Path(skill_info["path"])
        config = skill_info["config"]

        entry = config.get("entry", "scripts/run.py")
        entry_path = skill_path / entry

        if not entry_path.exists():
            return {"success": False, "error": f"技能入口不存在: {entry_path}"}

        cmd = ["python", str(entry_path)] + (args or [])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "技能执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def uninstall(self, skill_name: str) -> dict:
        """卸载技能"""
        if skill_name not in self._installed:
            return {"success": False, "error": f"技能未安装: {skill_name}"}

        skill_path = Path(self._installed[skill_name]["path"])
        if skill_path.exists():
            shutil.rmtree(skill_path)

        del self._installed[skill_name]
        print(f"✅ 技能已卸载: {skill_name}")
        return {"success": True}

    def get_info(self, skill_name: str) -> Optional[SkillInfo]:
        """获取技能信息"""
        if skill_name not in self._installed:
            return None

        config = self._installed[skill_name].get("config", {})
        return SkillInfo(
            name=skill_name,
            version=config.get("version", "1.0.0"),
            description=config.get("description", ""),
            description_en=config.get("description_en", ""),
            author=config.get("author", ""),
            category=config.get("category", "general"),
            tags=config.get("tags", []),
            installed=True,
            path=self._installed[skill_name].get("path", "")
        )
