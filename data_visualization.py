

import sys
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import csv



def read_bluetooth_data(port, baud_rate=9600, timeout=1):
    bluetooth_serial = None
    try:
        bluetooth_serial = serial.Serial(port, baud_rate, timeout=timeout)
        
        while True:
            data = bluetooth_serial.readline().decode().strip()
            if data.startswith("$:"):
                parts = data.split(':')[1].split(',')
                if len(parts) >= 3:  # Check for the correct number of gyro values
                    gyro_x = float(parts[0])
                    gyro_y = float(parts[1])
                    gyro_z = float(parts[2])
                    accel_x = float(parts[3])
                    accel_y = float(parts[4])
                    accel_z = float(parts[5])
                    mag_x = float(parts[6])
                    mag_y = float(parts[7])
                    mag_z = float(parts[8])
                    
                    # Get current timestamp
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Store data in CSV file
                    with open('data.csv', 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([current_time, gyro_x, gyro_y, gyro_z])
                        
                    # Also plot the data
                    print('Gyro X -', gyro_x)
                    print('Gyro y -', gyro_y)
                    print('Gyro Z -', gyro_z)
                    print('accel X - '+str(accel_x))
                    print('accel y - '+str(accel_y))
                    print('accel Z - '+str(accel_z))
                    yield gyro_x, gyro_y, gyro_z
    
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping the program.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if bluetooth_serial:
            bluetooth_serial.close()

class GraphApp:
    def __init__(self, root, bluetooth_port):
        self.root = root
        self.root.title("Gyro Data Visualization")
        
        self.fig, self.ax = plt.subplots(figsize=(15, 8))  # Set the figure size
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        self.y_vals_x = []
        self.y_vals_y = []
        self.y_vals_z = []
        
        self.data_generator = read_bluetooth_data(bluetooth_port)
        
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=1)
    
    def update_plot(self, i):
        gyro_x, gyro_y, gyro_z = next(self.data_generator)
        self.y_vals_x.append(gyro_x)
        self.y_vals_y.append(gyro_y)
        self.y_vals_z.append(gyro_z)
        
        if len(self.y_vals_x) > 120:
            self.y_vals_x.pop(0)
            self.y_vals_y.pop(0)
            self.y_vals_z.pop(0)
        
        self.ax.clear()
        self.ax.plot(self.y_vals_x, label='Gyro X-axis', color='blue')
        self.ax.plot(self.y_vals_y, label='Gyro Y-axis', color='green')
        self.ax.plot(self.y_vals_z, label='Gyro Z-axis', color='red')
        
        self.ax.set_ylabel("Gyro Data")
        self.ax.set_xlabel("Time")
        self.ax.set_title("Gyro Data Graph")
        self.ax.legend()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python data_visualization.py <serial_port>")
        sys.exit(1)


    bluetooth_port = sys.argv[1]

    root = tk.Tk()
    app = GraphApp(root, bluetooth_port)
    
    # Configure the root window to be full screen
    root.state('zoomed') 
    # root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda event: root.destroy())  # Exit full screen on pressing Esc
    root.mainloop()
