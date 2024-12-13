from flask import Flask, render_template, request, redirect, url_for, session, send_file
from PIL import Image
import io
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user credentials
USER_CREDENTIALS = {
    "admin": "password123",
    "hhh": "123"
}

def encode_message(image, message):
    # Convert image to RGB mode if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    pixels = image.load()
    
    message_bin = ''.join(format(ord(c), '08b') for c in message)  # Convert message to binary
    message_bin += '1111111111111110'  # Add delimiter to mark the end of the message
    
    data_index = 0
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]  # This will now work as the image is in RGB mode
            # Modify the LSB of each color channel with the message binary data
            if data_index < len(message_bin):
                r = (r & 0b11111110) | int(message_bin[data_index])  # Modify LSB of red
                data_index += 1
            if data_index < len(message_bin):
                g = (g & 0b11111110) | int(message_bin[data_index])  # Modify LSB of green
                data_index += 1
            if data_index < len(message_bin):
                b = (b & 0b11111110) | int(message_bin[data_index])  # Modify LSB of blue
                data_index += 1
            
            pixels[x, y] = (r, g, b)  # Save the new pixel values back to the image
    
    return image


def decode_message(image_path):
    image = Image.open(image_path)
    pixels = image.load()

    binary_message = ""
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            binary_message += bin(r)[-1]  # Extract LSB of red
            binary_message += bin(g)[-1]  # Extract LSB of green
            binary_message += bin(b)[-1]  # Extract LSB of blue

    # Find the delimiter and slice the binary message
    delimiter = "1111111111111110"
    if delimiter in binary_message:
        binary_message = binary_message[:binary_message.index(delimiter)]
    else:
        raise ValueError("No delimiter found in the image data")

    # Convert binary message to text
    decoded_message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        decoded_message += chr(int(byte, 2))
    return decoded_message



# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '123':  # Example credentials
            session['user'] = username  # Save user to session
            return redirect(url_for('steganography'))  # Redirect to the steganography page
        else:
            return render_template('login.html', error='Invalid username or password')  # Show error message

    return render_template('login.html')  # Render login page when GET request is made


@app.route('/steganography')
def steganography():
    if 'user' in session:  # Check if user is logged in
        return render_template('steganography.html')  # Show steganography page
    return redirect(url_for('login'))

@app.route('/encode', methods=['POST'])
def encode():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))
        image_file = request.files['image']
        if not image_file:
            return "No image file provided", 400
        message = request.form['message']
        image = Image.open(image_file.stream)
        encoded_image = encode_message(image, message)

        img_io = io.BytesIO()
        encoded_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='encoded_image.png')
    except Exception as e:
        print(f"Encoding error: {e}")
        return "An error occurred during encoding", 500


@app.route('/decode', methods=['POST'])
def decode():
    try:
        uploaded_image = request.files['encodedImage']
        if not uploaded_image or uploaded_image.filename == '':
            return "No file selected for decoding", 400

        # Save the uploaded file temporarily
        temp_dir = os.path.join('static', 'uploads')
        os.makedirs(temp_dir, exist_ok=True)  # Create directory if it doesn't exist
        image_path = os.path.join(temp_dir, uploaded_image.filename)
        uploaded_image.save(image_path)

        # Decode the message
        decoded_message = decode_message(image_path)
        os.remove(image_path)  # Clean up the temporary file

        return render_template('steganography.html', decoded_message=decoded_message)
    except Exception as e:
        print(f"Decoding error: {e}")
        return "An error occurred during decoding", 500


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)