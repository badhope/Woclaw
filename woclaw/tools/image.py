"""
图像处理工具
"""

from pathlib import Path
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class ImageTool(BaseTool):
    """
    图像处理工具
    """
    
    name: ClassVar[str] = "image"
    description: ClassVar[str] = "图像处理：调整大小、格式转换、裁剪、滤镜"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行图像处理操作
        
        Args:
            action: 操作类型
                - resize: 调整大小
                - convert: 格式转换
                - crop: 裁剪
                - rotate: 旋转
                - flip: 翻转
                - filter: 滤镜
                - info: 获取图像信息
                - thumbnail: 生成缩略图
        """
        handlers = {
            "resize": self._resize,
            "convert": self._convert,
            "crop": self._crop,
            "rotate": self._rotate,
            "flip": self._flip,
            "filter": self._filter,
            "info": self._info,
            "thumbnail": self._thumbnail,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    def _get_pil(self):
        try:
            from PIL import Image
            return Image
        except ImportError:
            raise ImportError("Please install Pillow: pip install Pillow")
    
    async def _resize(
        self,
        source: str,
        output: str,
        width: int | None = None,
        height: int | None = None,
        keep_aspect: bool = True
    ) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            img = Image.open(source)
            
            if keep_aspect and width and height:
                img.thumbnail((width, height))
            elif width and height:
                img = img.resize((width, height))
            elif width:
                ratio = width / img.width
                img = img.resize((width, int(img.height * ratio)))
            elif height:
                ratio = height / img.height
                img = img.resize((int(img.width * ratio), height))
            
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            img.save(output)
            
            return {
                "success": True,
                "output": output,
                "size": img.size,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _convert(
        self,
        source: str,
        output: str,
        format: str | None = None
    ) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            img = Image.open(source)
            
            if not format:
                format = Path(output).suffix[1:].upper()
            
            if format.upper() == "JPG":
                format = "JPEG"
            
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            img.save(output, format=format)
            
            return {
                "success": True,
                "output": output,
                "format": format,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _crop(
        self,
        source: str,
        output: str,
        left: int,
        top: int,
        right: int,
        bottom: int
    ) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            img = Image.open(source)
            cropped = img.crop((left, top, right, bottom))
            
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            cropped.save(output)
            
            return {
                "success": True,
                "output": output,
                "size": cropped.size,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _rotate(
        self,
        source: str,
        output: str,
        angle: float,
        expand: bool = True
    ) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            img = Image.open(source)
            rotated = img.rotate(angle, expand=expand)
            
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            rotated.save(output)
            
            return {
                "success": True,
                "output": output,
                "angle": angle,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _flip(
        self,
        source: str,
        output: str,
        direction: str = "horizontal"
    ) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            img = Image.open(source)
            
            if direction == "horizontal":
                flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            flipped.save(output)
            
            return {
                "success": True,
                "output": output,
                "direction": direction,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _filter(
        self,
        source: str,
        output: str,
        filter_type: str
    ) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            from PIL import ImageFilter
            
            img = Image.open(source)
            
            filters = {
                "blur": ImageFilter.BLUR,
                "sharpen": ImageFilter.SHARPEN,
                "edge_enhance": ImageFilter.EDGE_ENHANCE,
                "emboss": ImageFilter.EMBOSS,
                "smooth": ImageFilter.SMOOTH,
                "contour": ImageFilter.CONTOUR,
                "find_edges": ImageFilter.FIND_EDGES,
            }
            
            if filter_type not in filters:
                return {"success": False, "error": f"Unknown filter: {filter_type}"}
            
            filtered = img.filter(filters[filter_type])
            
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            filtered.save(output)
            
            return {
                "success": True,
                "output": output,
                "filter": filter_type,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _info(self, source: str) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            img = Image.open(source)
            
            return {
                "success": True,
                "path": source,
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _thumbnail(
        self,
        source: str,
        output: str,
        size: tuple[int, int] = (128, 128)
    ) -> dict[str, Any]:
        try:
            Image = self._get_pil()
            img = Image.open(source)
            img.thumbnail(size)
            
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            img.save(output)
            
            return {
                "success": True,
                "output": output,
                "size": img.size,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
