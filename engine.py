from PIL import Image, ImageDraw, ImageFont
import utils
import os

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    if len(hex_code) != 6:
        return (255, 255, 255)
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def create_ascii_art(text, font_name, font_size, aspect, charset, color_start, color_end, direction, shadow=False, shadow_offset_x=2, shadow_offset_y=1, letter_spacing=0, line_spacing=0):
    try:
        try:
            # もし font_name 自体が有効なパスならそのまま使う
            if os.path.exists(font_name):
                font_path = font_name
            else:
                font_path = utils.get_font_path(font_name)
            
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 最終フォールバック。ここでNullだと英語しか出ない
                font = ImageFont.load_default()
        except Exception as e:
            utils.log_error(f"Font load error ({font_name}): {e}")
            font = ImageFont.load_default()

        lines = text.split('\n')
        dummy_img = Image.new("L", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        margin = font_size * 2
        max_w = 0
        
        for line in lines:
            lw = sum(int(dummy_draw.textlength(c, font=font)) for c in line) + max(0, len(line)-1) * letter_spacing
            max_w = max(max_w, lw)
            
        # Pylanceエラー対策: 属性の存在をチェックしてからアクセスするよ
        if hasattr(font, 'getmetrics'):
            ascent, descent = font.getmetrics() # type: ignore
            lh = ascent + descent
        else:
            lh = font_size

        total_h = len(lines) * lh + max(0, len(lines)-1) * line_spacing
        
        canvas_w = max(1, max_w + margin * 2)
        canvas_h = max(1, total_h + margin * 2)
        
        img = Image.new("L", (canvas_w, canvas_h), 0)
        draw = ImageDraw.Draw(img)
        
        current_y = margin
        for line in lines:
            current_x = margin
            for char in line:
                draw.text((current_x, current_y), char, font=font, fill=255)
                cw = int(draw.textlength(char, font=font))
                current_x += cw + letter_spacing
            current_y += lh + line_spacing
            
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            w, h = img.size
        else:
            w, h = 1, 1
            img = Image.new("L", (1, 1), 0)

        new_w = max(1, int(w * aspect))
        img = img.resize((new_w, int(h)), Image.Resampling.NEAREST)

        rgb_start = hex_to_rgb(color_start)
        rgb_end = hex_to_rgb(color_end)

        shades = [" ", "░", "▒", "▓", "█"]
        
        base_aa = []
        for y in range(h):
            row_data = []
            for x in range(new_w):
                pixel_val = img.getpixel((x, y))
                
                if isinstance(pixel_val, tuple):
                    pixel = int(pixel_val[0])
                elif pixel_val is not None:
                    pixel = int(pixel_val)
                else:
                    pixel = 0
                
                if charset == "gradient":
                    idx = int((pixel / 255) * 4)
                    char = shades[idx]
                else:
                    char = "█" if pixel > 127 else " "

                if char != " ":
                    if direction == "horizontal":
                        ratio = x / max(1, new_w - 1)
                    else:
                        ratio = y / max(1, h - 1)
                        
                    r = int(rgb_start[0] + (rgb_end[0] - rgb_start[0]) * ratio)
                    g = int(rgb_start[1] + (rgb_end[1] - rgb_start[1]) * ratio)
                    b = int(rgb_start[2] + (rgb_end[2] - rgb_start[2]) * ratio)
                    color = (r, g, b)
                    row_data.append((char, color))
                else:
                    row_data.append((" ", (0, 0, 0)))
            base_aa.append(row_data)

        if shadow:
            pad = 1
            main_shift_x = pad + max(0, -shadow_offset_x)
            main_shift_y = pad + max(0, -shadow_offset_y)
            shad_shift_x = pad + max(0, shadow_offset_x)
            shad_shift_y = pad + max(0, shadow_offset_y)
            
            final_w = new_w + pad * 2 + abs(shadow_offset_x)
            final_h = h + pad * 2 + abs(shadow_offset_y)
            final_data = [[(" ", (0, 0, 0)) for _ in range(final_w)] for _ in range(final_h)]
            
            for y in range(-pad, h + pad):
                for x in range(-pad, new_w + pad):
                    is_empty = True
                    if 0 <= y < h and 0 <= x < new_w:
                        is_empty = (base_aa[y][x][0] == " ")
                        
                    if is_empty:
                        touches = False
                        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < h and 0 <= nx < new_w and base_aa[ny][nx][0] != " ":
                                touches = True
                                break
                        
                        if touches:
                            sy = y + shad_shift_y
                            sx = x + shad_shift_x
                            
                            cx = max(0, min(x, new_w - 1))
                            cy = max(0, min(y, h - 1))
                            if direction == "horizontal":
                                ratio = cx / max(1, new_w - 1)
                            else:
                                ratio = cy / max(1, h - 1)
                            r = int(rgb_start[0] + (rgb_end[0] - rgb_start[0]) * ratio)
                            g = int(rgb_start[1] + (rgb_end[1] - rgb_start[1]) * ratio)
                            b = int(rgb_start[2] + (rgb_end[2] - rgb_start[2]) * ratio)
                            
                            final_data[sy][sx] = ("█", (r, g, b))
                            
            for y in range(h):
                for x in range(new_w):
                    char, color = base_aa[y][x]
                    if char != " ":
                        my = y + main_shift_y
                        mx = x + main_shift_x
                        final_data[my][mx] = (char, color)
        else:
            final_data = base_aa
            final_w = new_w
            final_h = h

        plain_lines = []
        ansi_lines = []
        
        for y in range(final_h):
            p_line = ""
            a_line = ""
            prev_color = None
            for x in range(final_w):
                char, color = final_data[y][x]
                p_line += char
                if char != " ":
                    if color != prev_color:
                        a_line += f"\033[38;2;{color[0]};{color[1]};{color[2]}m{char}"
                        prev_color = color
                    else:
                        a_line += char
                else:
                    a_line += " "
            plain_lines.append(p_line)
            ansi_lines.append(a_line + "\033[0m")

        try:
            aa_font = ImageFont.truetype("consola.ttf", 14)
        except Exception:
            aa_font = ImageFont.load_default()

        dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        char_bbox = dummy_draw.textbbox((0, 0), "█", font=aa_font)
        char_w = max(1, int(char_bbox[2] - char_bbox[0]))
        char_h = max(1, int(char_bbox[3] - char_bbox[1]))
        
        canvas_w = final_w * char_w
        canvas_h = final_h * char_h
        
        out_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        out_draw = ImageDraw.Draw(out_img)
        
        for y, row in enumerate(final_data):
            for x, (char, color) in enumerate(row):
                if char != " ":
                    out_draw.text((x * char_w, y * char_h), char, font=aa_font, fill=color)

        return "\n".join(plain_lines), "\n".join(ansi_lines), out_img
        
    except Exception as e:
        utils.log_error(f"Engine crash: {e}")
        raise e