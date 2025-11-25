import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading

class SketchAnimatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Sketch Animator")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.image = None
        self.canvas_img = None
        self.contours = None
        self.is_animating = False
        self.animation_thread = None
        self.current_frame = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top control panel
        control_frame = tk.Frame(self.root, bg='#3c3c3c', height=80)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        # Buttons
        btn_base_style = {'font': ('Arial', 11, 'bold'), 'fg': 'white', 
                          'cursor': 'hand2', 'relief': 'flat',
                          'padx': 20, 'pady': 10}
        
        self.load_btn = tk.Button(control_frame, text="📁 Load Image", 
                                   command=self.load_image, 
                                   bg='#4CAF50', activebackground='#45a049',
                                   **btn_base_style)
        self.load_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        self.start_btn = tk.Button(control_frame, text="▶ Start Animation", 
                                    command=self.start_animation, state=tk.DISABLED,
                                    bg='#2196F3', activebackground='#0b7dda', 
                                    **btn_base_style)
        self.start_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        self.stop_btn = tk.Button(control_frame, text="⏸ Stop", 
                                   command=self.stop_animation, state=tk.DISABLED,
                                   bg='#f44336', activebackground='#da190b', 
                                   **btn_base_style)
        self.stop_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        self.reset_btn = tk.Button(control_frame, text="🔄 Reset", 
                                    command=self.reset_canvas, state=tk.DISABLED,
                                    bg='#FF9800', activebackground='#e68900', 
                                    **btn_base_style)
        self.reset_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Speed control
        speed_frame = tk.Frame(control_frame, bg='#3c3c3c')
        speed_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(speed_frame, text="Speed:", bg='#3c3c3c', 
                fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.IntVar(value=5)
        self.speed_scale = tk.Scale(speed_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                     variable=self.speed_var, bg='#3c3c3c', fg='white',
                                     highlightthickness=0, length=150, troughcolor='#555')
        self.speed_scale.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Ready", bg='#3c3c3c',
                                      fg='#4CAF50', font=('Arial', 11, 'bold'))
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Main display area
        display_frame = tk.Frame(self.root, bg='#2b2b2b')
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Original image panel
        left_frame = tk.LabelFrame(display_frame, text="Original Image", 
                                    bg='#3c3c3c', fg='white', font=('Arial', 11, 'bold'))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_label = tk.Label(left_frame, bg='#1e1e1e', 
                                        text="No image loaded", fg='gray')
        self.original_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sketch panel
        right_frame = tk.LabelFrame(display_frame, text="Sketch Animation", 
                                     bg='#3c3c3c', fg='white', font=('Arial', 11, 'bold'))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.sketch_label = tk.Label(right_frame, bg='#1e1e1e',
                                      text="Sketch will appear here", fg='gray')
        self.sketch_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.image = cv2.imread(file_path)
        
        if self.image is None:
            messagebox.showerror("Error", "Could not load image!")
            return
        
        # Resize for better performance
        max_dim = 800
        h, w = self.image.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            self.image = cv2.resize(self.image, None, fx=scale, fy=scale)
        
        # Display original image
        self.display_image(self.image, self.original_label)
        
        # Process image for sketch
        self.process_image()
        
        self.status_label.config(text="Image loaded ✓", fg='#4CAF50')
        self.start_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)
        
    def display_image(self, cv_img, label):
        # Convert BGR to RGB
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        
        # Resize to fit label
        label_width = label.winfo_width() - 20
        label_height = label.winfo_height() - 20
        
        if label_width > 1 and label_height > 1:
            pil_img.thumbnail((label_width, label_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(pil_img)
        label.config(image=photo, text="")
        label.image = photo
        
    def process_image(self):
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection with optimized parameters
        edges = cv2.Canny(gray, 80, 150)
        
        # Find contours with approximation for speed
        self.contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                            cv2.CHAIN_APPROX_SIMPLE)
        
        # Create blank canvas
        self.canvas_img = np.zeros_like(self.image)
        
    def start_animation(self):
        if self.is_animating:
            return
        
        self.is_animating = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.load_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Animating...", fg='#2196F3')
        
        # Start animation in separate thread
        self.animation_thread = threading.Thread(target=self.animate_sketch, daemon=True)
        self.animation_thread.start()
        
    def animate_sketch(self):
        # Create working canvas
        canvas = np.zeros_like(self.image)
        
        # Calculate batch size based on speed
        batch_size = self.speed_var.get()
        
        for contour in self.contours:
            if not self.is_animating:
                break
            
            # Draw multiple points per frame for speed
            for i in range(1, len(contour), max(1, batch_size)):
                if not self.is_animating:
                    break
                
                # Draw batch of lines
                end_idx = min(i + batch_size, len(contour))
                for j in range(i, end_idx):
                    if j > 0:
                        x1, y1 = contour[j-1][0]
                        x2, y2 = contour[j][0]
                        cv2.line(canvas, (x1, y1), (x2, y2), (255, 255, 255), 1)
                
                # Update display
                self.current_frame = canvas.copy()
                self.root.after(0, self.update_sketch_display)
        
        # Animation complete
        if self.is_animating:
            self.root.after(0, self.animation_complete)
            
    def update_sketch_display(self):
        if self.current_frame is not None:
            self.display_image(self.current_frame, self.sketch_label)
            
    def animation_complete(self):
        self.is_animating = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Animation complete ✓", fg='#4CAF50')
        
    def stop_animation(self):
        self.is_animating = False
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)
        self.load_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Stopped", fg='#FF9800')
        
    def reset_canvas(self):
        self.stop_animation()
        if self.canvas_img is not None:
            self.canvas_img = np.zeros_like(self.image)
            self.current_frame = self.canvas_img.copy()
            self.update_sketch_display()
            self.status_label.config(text="Reset ✓", fg='#4CAF50')

if __name__ == "__main__":
    root = tk.Tk()
    app = SketchAnimatorApp(root)
    root.mainloop()