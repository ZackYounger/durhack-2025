import tkinter as tk
import math

# Create main window and canvas
root = tk.Tk()
root.title("1 cm Checkerboard")
root.attributes("-fullscreen", True)

canvas = tk.Canvas(root, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# state for fullscreen toggle
is_fullscreen = True

_redraw_after_id = None

def get_pixels_per_cm():
    # Tk understands units; '1c' is 1 centimeter
    try:
        ppc = root.winfo_fpixels('1c')
        # ensure positive integer pixel size
        return max(1, int(round(ppc)))
    except Exception:
        # fallback: assume 96 dpi -> 96/2.54 px/cm ≈ 37.8
        return int(round(96.0 / 2.54))

def draw_checker():
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width <= 0 or height <= 0:
        return
    square = get_pixels_per_cm()
    cols = math.ceil(width / square)
    rows = math.ceil(height / square)
    # Draw rectangles; alternate colors
    for r in range(rows):
        y0 = r * square
        y1 = y0 + square
        for c in range(cols):
            x0 = c * square
            x1 = x0 + square
            color = "#000000" if (r + c) % 2 == 0 else "#ffffff"
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)
    # If screen not an exact multiple, last rows/cols extend beyond; that's fine.

def schedule_redraw(event=None):
    global _redraw_after_id
    # debounce rapid Configure events
    if _redraw_after_id is not None:
        root.after_cancel(_redraw_after_id)
    _redraw_after_id = root.after(80, draw_checker)

def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)
    schedule_redraw()

def exit_app(event=None):
    root.destroy()

# Bindings
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_app)
root.bind("<Configure>", schedule_redraw)

# Initial draw after window initialized
root.after(100, draw_checker)

if __name__ == "__main__":
    root.mainloop()
