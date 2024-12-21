import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import *
from qrcode.image.styles.colormasks import *
from PIL import Image
import io
from typing import Optional, Dict, Any

class QRCodeGenerator:
    @staticmethod
    def create_qr_code(
        data: str,
        style_config: Dict[str, Any],
        logo_path: Optional[str] = None
    ) -> bytes:
        """
        Create a QR code with custom styling and optional logo.
        
        Args:
            data: The data to encode in the QR code
            style_config: Dictionary containing style configuration
            logo_path: Optional path to logo image
            
        Returns:
            bytes: The QR code image in bytes
        """
        # QR code basic configuration
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Style configuration
        style_mapping = {
            'square': SquareModuleDrawer(),
            'gapped': GappedSquareModuleDrawer(),
            'circle': CircleModuleDrawer(),
            'rounded': RoundedModuleDrawer(),
            'vertical': VerticalBarsDrawer(),
            'horizontal': HorizontalBarsDrawer(),
        }

        color_mapping = {
            'solid': SolidFillColorMask,
            'radial': RadialGradiantColorMask,
            'square': SquareGradiantColorMask,
            'horizontal': HorizontalGradiantColorMask,
            'vertical': VerticalGradiantColorMask,
        }

        # Apply style configuration
        module_drawer = style_mapping.get(style_config.get('style', 'square'))
        color_mask_class = color_mapping.get(style_config.get('color_type', 'solid'))
        
        # Handle color configuration
        if color_mask_class == SolidFillColorMask:
            color_mask = color_mask_class(
                front_color=style_config.get('front_color', '#000000'),
                back_color=style_config.get('back_color', '#FFFFFF')
            )
        else:
            color_mask = color_mask_class(
                back_color=style_config.get('back_color', '#FFFFFF'),
                center_color=style_config.get('center_color', '#000000'),
                edge_color=style_config.get('edge_color', '#000000')
            )

        # Create QR code image
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer,
            color_mask=color_mask,
        )

        # Add logo if provided
        if logo_path:
            try:
                logo = Image.open(logo_path)
                # Calculate logo size (max 30% of QR code)
                logo_size = int(min(img.size) * 0.3)
                logo = logo.resize((logo_size, logo_size))
                
                # Calculate position to center logo
                pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
                
                # Create white background for logo
                logo_bg = Image.new('RGBA', (logo_size, logo_size), 'white')
                logo_bg.paste(logo, (0, 0), logo)
                
                # Paste logo onto QR code
                img.paste(logo_bg, pos)
            except Exception as e:
                print(f"Error adding logo to QR code: {e}")

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()

    @staticmethod
    def validate_style_config(style_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize style configuration.
        
        Args:
            style_config: Dictionary containing style configuration
            
        Returns:
            Dict[str, Any]: Validated style configuration
        """
        valid_styles = {'square', 'gapped', 'circle', 'rounded', 'vertical', 'horizontal'}
        valid_color_types = {'solid', 'radial', 'square', 'horizontal', 'vertical'}
        
        # Validate and set defaults
        validated = {
            'style': style_config.get('style', 'square'),
            'color_type': style_config.get('color_type', 'solid'),
            'front_color': style_config.get('front_color', '#000000'),
            'back_color': style_config.get('back_color', '#FFFFFF'),
            'center_color': style_config.get('center_color', '#000000'),
            'edge_color': style_config.get('edge_color', '#000000'),
        }
        
        # Ensure valid style
        if validated['style'] not in valid_styles:
            validated['style'] = 'square'
            
        # Ensure valid color type
        if validated['color_type'] not in valid_color_types:
            validated['color_type'] = 'solid'
            
        # Validate color formats (basic check)
        for color_key in ['front_color', 'back_color', 'center_color', 'edge_color']:
            if not validated[color_key].startswith('#'):
                validated[color_key] = '#000000'
                
        return validated 