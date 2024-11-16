import datetime as dt
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Конфигурация API
url = "https://api.trongrid.io/v1/accounts/TKiPsLhSKhcYS9uWkGet1yV82n6TMS8cA9/transactions/trc20"
pages = 3
params = {
    'only_confirmed': True,
    'limit': 20,
}

# Функция для получения списка транзакций
def get_transactions():
    num = 0
    transactions = []

    for _ in range(pages):
        response = requests.get(url, params=params, headers={"accept": "application/json"})
        data = response.json()

        # Обновляем fingerprint для пагинации
        params['fingerprint'] = data.get('meta', {}).get('fingerprint')

        # Проверка наличия данных
        if 'data' not in data:
            break

        for tr in data.get('data', []):
            num += 1
            transaction_id = tr.get('transaction_id')
            symbol = tr.get('token_info', {}).get('symbol')
            from_addr = tr.get('from')
            to_addr = tr.get('to')
            value = tr.get('value', '')
            decimals = int(tr.get('token_info', {}).get('decimals', '6'))
            amount = float(value[: -decimals] + '.' + value[-decimals:])
            timestamp = dt.datetime.fromtimestamp(float(tr.get('block_timestamp', '')) / 1000)

            # Добавляем транзакцию в список
            transactions.append({
                "transaction_id": transaction_id,
                # "symbol": symbol,
                # "from": from_addr,
                # "to": to_addr,
                # "amount": amount,
                # "timestamp": timestamp
            })

    return transactions

@app.route('/check_transaction', methods=['GET'])
def check_transaction():
    try:
        hash_id = request.args.get('hash')

        if not hash_id:
            return jsonify({"status": "error", "message": "Hash parameter is missing"}), 400

        print(f"Received hash: {hash_id}")

        # Получаем список транзакций
        transactions = get_transactions()
        print(f"Fetched transactions: {len(transactions)}")

        # Проверяем наличие транзакции с указанным хэшем
        for tr in transactions:
            print(f"Checking transaction: {tr['transaction_id']}")
            if tr["transaction_id"] == hash_id:
                return jsonify({"status": "Success", "transaction": tr}), 200

        # Если не нашли транзакцию
        return jsonify({"status": "Failed", "message": "Transaction not found"}), 404

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Запуск сервера Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)
