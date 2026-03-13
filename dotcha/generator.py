import io
import random
import string
import asyncio
from typing import Tuple, Union, Optional, List
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

from .theme import ColorSchema, Theme, Difficulty, LIGHT_SCHEMA, DARK_SCHEMA
from .shapes import Shape, Circle, Triangle, Line, Square, Star


class CaptchaGenerator:
    """
    Advanced Gestalt Illusion Captcha Generator.
    Supports Distortion, GIFs, and Difficulty Levels.
    """

    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 200
    
    DIFFICULTY_CONFIG = {
        Difficulty.EASY: {"shapes": 8000, "text_size_range": (3, 4), "bg_size_range": (1, 2)},
        Difficulty.MEDIUM: {"shapes": 5000, "text_size_range": (3, 5), "bg_size_range": (2, 4)},
        Difficulty.HARD: {"shapes": 3500, "text_size_range": (2, 4), "bg_size_range": (3, 6)},
    }
    
    def __init__(
        self, 
        theme: Union[str, Theme, ColorSchema] = Theme.LIGHT,
        difficulty: Difficulty = Difficulty.MEDIUM,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        char_length: int = 5,
        font_size: Optional[int] = None
    ):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.char_length = char_length
        self.schema = self._get_schema(theme)
        
        # Adaptive font size if not provided (approx 40% of height)
        self.font_size = font_size or int(height * 0.45)
        self._font = self._load_font(self.font_size)
        self._config = self.DIFFICULTY_CONFIG[difficulty]

    def _get_schema(self, theme: Union[str, Theme, ColorSchema]) -> ColorSchema:
        if isinstance(theme, ColorSchema):
            return theme
        
        theme_val = theme.value if isinstance(theme, Theme) else theme
        if theme_val == Theme.DARK.value:
            return DARK_SCHEMA
        
        return LIGHT_SCHEMA

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        # Support multiple common fonts or fallback
        font_names = ["arial.ttf", "DejaVuSans.ttf", "Verdana.ttf", "tahoma.ttf"]
        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _generate_text(self, length: int = 5) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def _apply_distortion(self, image: Image.Image) -> Image.Image:
        """Apply mesh distortion to the mask image."""
        # Simple waviness
        width, height = image.size
        # Create a copy as we are working with pixel data
        distorted = image.copy()
        # In practice, ImageOps.deform or custom transform is better
        # For POC, we'll use a simple affine transform for slight slant/shear
        shear_factor = random.uniform(-0.2, 0.2)
        distorted = distorted.transform(
            (width, height), 
            Image.AFFINE, 
            (1, shear_factor, 0, 0, 1, 0),
            resample=Image.BICUBIC
        )
        return distorted

    def _add_glitches(self, draw: ImageDraw.ImageDraw, mask_pixels: any):
        """Add lines that cross characters to confuse OCR."""
        for _ in range(random.randint(3, 7)):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = x1 + random.randint(-50, 50)
            y2 = y1 + random.randint(-30, 30)
            
            # Draw on mask if we wanted to affect shape logic, 
            # but here we just draw some random shapes on the canvas later
            pass

    def _render(self, frames: int = 1) -> Tuple[str, Union[io.BytesIO, List[io.BytesIO]]]:
        """
        Rendering logic. If frames > 1, returns frames for GIF.
        """
        text = self._generate_text(length=self.char_length)
        
        # 1. Create mask with distortion
        base_mask = Image.new('L', (self.width, self.height), 0)
        mask_draw = ImageDraw.Draw(base_mask)
        
        text_bbox = mask_draw.textbbox((0, 0), text, font=self._font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        pos = ((self.width - text_width) // 2, (self.height - text_height) // 2)
        mask_draw.text(pos, text, font=self._font, fill=255)
        
        mask = self._apply_distortion(base_mask)
        mask_pixels = mask.load()

        # 2. Render logic
        def draw_frame(frame_idx: int) -> Image.Image:
            canvas = Image.new('RGB', (self.width, self.height), self.schema.background)
            draw = ImageDraw.Draw(canvas, 'RGBA')
            shape_types = [Circle, Triangle, Line, Square, Star]
            
            shapes_to_draw = self._config["shapes"]
            
            for i in range(shapes_to_draw):
                # For GIF animation, background shapes drift, text shapes stay fixed
                jitter_x = 0
                jitter_y = 0
                
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                
                mask_val = mask_pixels[x, y]
                is_text = mask_val > 128
                
                if is_text and frames > 1:
                    # Temporal Sparsity: Only show ~40% of the text in any single frame
                    # The human brain integrates this over time, but OCR sees a broken pattern
                    if random.random() > 0.4:
                        continue
                
                if not is_text and frames > 1:
                    # Drift background shapes based on frame index with some randomness
                    x = (x + frame_idx * random.randint(3, 7)) % self.width
                
                color_list = self.schema.text_colors if is_text else self.schema.background_colors
                color = random.choice(color_list)
                
                shape_cls = random.choice(shape_types)
                if is_text:
                    size = random.randint(*self._config["text_size_range"])
                else:
                    size = random.randint(*self._config["bg_size_range"])
                
                shape = shape_cls(x, y, size)
                shape.draw(draw, color)
            
            return canvas

        if frames == 1:
            canvas = draw_frame(0)
            buffer = io.BytesIO()
            canvas.save(buffer, format='PNG')
            buffer.seek(0)
            
            mask.close()
            base_mask.close()
            canvas.close()
            return text, buffer
        
        # Multiple frames for GIF
        rendered_frames = []
        for f in range(frames):
            rendered_frames.append(draw_frame(f))
            
        buffer = io.BytesIO()
        rendered_frames[0].save(
            buffer,
            format='GIF',
            save_all=True,
            append_images=rendered_frames[1:],
            duration=100,
            loop=0
        )
        buffer.seek(0)
        
        # Cleanup
        mask.close()
        base_mask.close()
        for f in rendered_frames:
            f.close()
            
        return text, buffer

    def generate(self) -> Tuple[str, io.BytesIO]:
        return self._render(frames=1)

    async def agenerate(self) -> Tuple[str, io.BytesIO]:
        return await asyncio.to_thread(self._render, frames=1)

    def generate_gif(self, frames: int = 8) -> Tuple[str, io.BytesIO]:
        return self._render(frames=frames)

    async def agenerate_gif(self, frames: int = 8) -> Tuple[str, io.BytesIO]:
        return await asyncio.to_thread(self._render, frames=frames)

    @staticmethod
    def check_answer(user_input: str, actual: str, fuzzy_tolerance: int = 0) -> Tuple[bool, int]:
        """
        Validates the user's answer.
        Returns Tuple[is_correct, distance].
        Distance is Levenshtein distance.
        """
        s1 = user_input.strip().upper()
        s2 = actual.strip().upper()
        
        # Calculate Levenshtein Distance
        if len(s1) < len(s2):
            return CaptchaGenerator.check_answer(s2, s1, fuzzy_tolerance)[0:2]

        if len(s2) == 0:
            return s1 == s2, len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        distance = previous_row[-1]
        is_correct = distance <= fuzzy_tolerance
        
        return is_correct, distance
