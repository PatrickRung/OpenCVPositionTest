#!/usr/bin/env python3
"""
Duet M559 File Upload Script
Uploads a file to a Duet board via USB serial using the M559 command.
"""

import serial
import time
import argparse
import os
import sys


def send_gcode(ser, command, wait_for_ok=True, timeout=5):
    """Send a GCode command and optionally wait for 'ok' response."""
    # Ensure command ends with newline
    if not command.endswith('\n'):
        command += '\n'
    
    ser.write(command.encode('utf-8'))
    print(f"Sent: {command.strip()}")
    
    if wait_for_ok:
        start_time = time.time()
        response = ""
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                response += chunk
                print(f"Response: {chunk}", end='')
                
                if 'ok' in response.lower() or 'error' in response.lower():
                    return response
            time.sleep(0.1)
        
        print(f"Warning: Timeout waiting for response to: {command.strip()}")
        return response
    
    return None


def upload_file_m559(port, filename, destination_path, baudrate=115200):
    """
    Upload a file to Duet board using M559 command.
    
    Args:
        port: Serial port (e.g., '/dev/ttyACM0' or 'COM3')
        filename: Local file path to upload
        destination_path: Destination path on Duet (e.g., '0:/gcodes/myfile.g')
        baudrate: Serial baud rate (default 115200)
    """
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found!")
        return False
    
    # Get file size
    file_size = os.path.getsize(filename)
    print(f"File: {filename}")
    print(f"Size: {file_size} bytes")
    print(f"Destination: {destination_path}")
    
    try:
        # Open serial connection
        print(f"\nOpening serial port {port} at {baudrate} baud...")
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for connection to stabilize
        
        # Flush any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Test connection
        print("\nTesting connection...")
        response = send_gcode(ser, "M115")  # Get firmware version
        
        # Send M559 command to initiate file upload
        m559_command = f'M559 P"{destination_path}" S{file_size}'
        print(f"\nInitiating file upload with: {m559_command}")
        response = send_gcode(ser, m559_command, timeout=3)
        
        if response and 'error' in response.lower():
            print(f"Error initiating upload: {response}")
            return False
        
        # Read and send file content
        print(f"\nUploading file content...")
        with open(filename, 'rb') as f:
            bytes_sent = 0
            chunk_size = 512  # Send in chunks
            
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                ser.write(chunk)
                bytes_sent += len(chunk)
                
                # Show progress
                progress = (bytes_sent / file_size) * 100
                print(f"\rProgress: {bytes_sent}/{file_size} bytes ({progress:.1f}%)", end='')
                
                # Small delay to avoid overwhelming the buffer
                time.sleep(0.01)
        
        print("\n\nFile content sent. Waiting for confirmation...")
        
        # Wait for upload to complete
        time.sleep(1)
        
        # Read any remaining response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"Final response: {response}")
        
        print("\nUpload complete!")
        
        # Close connection
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"\nSerial port error: {e}")
        return False
    except Exception as e:
        print(f"\nError during upload: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Upload a file to Duet board via USB serial using M559 command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python %(prog)s /dev/ttyACM0 myfile.gcode -d "0:/gcodes/myfile.gcode"
  python %(prog)s COM3 test.g -d "0:/macros/test.g" -b 115200
  
Notes:
  - The destination path should include the SD card prefix (0:/ or 1:/)
  - Common destinations:
    - GCode files: 0:/gcodes/filename.gcode
    - Macros: 0:/sys/filename.g or 0:/macros/filename.g
    - System files: 0:/sys/filename.g
        '''
    )
    
    parser.add_argument('port', help='Serial port (e.g., /dev/ttyACM0 or COM3)')
    parser.add_argument('file', help='File to upload')
    parser.add_argument('-d', '--destination', required=True,
                        help='Destination path on Duet (e.g., "0:/gcodes/myfile.g")')
    parser.add_argument('-b', '--baudrate', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    
    args = parser.parse_args()
    
    success = upload_file_m559(
        args.port,
        args.file,
        args.destination,
        args.baudrate
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()