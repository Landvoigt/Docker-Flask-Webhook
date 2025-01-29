import hmac
import hashlib
import subprocess
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

GITHUB_SECRET = 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/webhook/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        header_signature = request.headers.get('X-Hub-Signature-256')
        if not header_signature:
            logger.error('Signature missing')
            return jsonify({'error': 'Signature missing'}), 400

        sha_name, signature = header_signature.split('=')
        if sha_name != 'sha256':
            logger.error('Unsupported hash algorithm')
            return jsonify({'error': 'Unsupported hash algorithm'}, status=400)

        mac = hmac.new(
            GITHUB_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256
        )
        if not hmac.compare_digest(mac.hexdigest(), signature):
            logger.error('Invalid signature')
            return jsonify({'error': 'Invalid signature'}), 403

        payload = request.get_json()
        logger.info(f"Received payload: {payload}")

        try:
            logger.info('Triggering restart script...')
            subprocess.run(['/srv/projects/devknowhow/deploy_devknowhow.sh'], check=True)

            logger.info('Webhook processing completed successfully.')
            return jsonify({'status': 'success'}), 200

        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred: {e}")
            return jsonify({'error': 'Command failed', 'details': str(e)}), 500

    return jsonify({'error': 'Invalid method'}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
