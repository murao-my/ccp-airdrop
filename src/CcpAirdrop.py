from copyreg import constructor
from web3 import Web3
from web3.datastructures import AttributeDict
from eth_account.messages import encode_defunct
import json
import requests
import datetime
import src.config
from src.MyHDWallet import *
import datetime
import time

class CcpAirdrop():
    
    def __init__(self):
        self.wallet = MyHDWallet()
        self.wallet.SetMnemonic(src.config.getMnemonicPhrase())

        self.startAddressIndex = src.config.startAddressIndex()
        self.maxAddressIndex = src.config.maxAddressIndex()
        self.airdropInterval = src.config.airdropInterval()
        self.wallet_nonces = {}

        chain = "MCHV"
        self.web3 = Web3(Web3.HTTPProvider(src.config.getNetworkURL(chain)))       
        self.isConnected = self.web3.isConnected()
        if self.isConnected == False:
            print('connection fail')
            # abiの読み込み、アドレス設定は行うため、returnしない
            # return

        with open('./abi/MCHV.airdrop.json') as f:
            self.MchvAirdropAbi = json.load(f)

        self.airdropAddr = Web3.toChecksumAddress(src.config.TokenAddress.MCHV_airdropAddr)

    def LogTime(self):
        return datetime.datetime.now()
    
    def keepNonce(self):
        start = self.startAddressIndex
        end = self.maxAddressIndex
        cnt = end - start + 1

        print(f'{self.LogTime()} keepNonce start')

        try:
            for i in range(cnt):
                time.sleep(0.1)
                address_index = i + start
                account = self.wallet.GetAddress(address_index)
                walletAddr = account.p2pkh_address()

                nonce = self.web3.eth.getTransactionCount(walletAddr)
                self.wallet_nonces[address_index] = nonce
        except Exception as e:
            print(f'{self.LogTime()} keepNonce error：{e}')

    def getNonce(self, address_index, walletAddr):
        if address_index in self.wallet_nonces:
            return self.wallet_nonces[address_index]
        else:
            nonce = self.web3.eth.getTransactionCount(walletAddr)
            return nonce

    def airdropWaiting(self):
        # 待機する時間を設定（6:00）UTC時間
        target_time = datetime.datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)

        # 現在の時間を取得
        current_time = datetime.datetime.now()

        # 時間差を計算
        time_difference = (target_time - current_time).total_seconds()

        print(f'{self.LogTime()} airdropWaiting start:{time_difference}')

        # 過ぎた場合はマイナス
        if time_difference < 0:
            print(f"passed. return.")
            return

        # 正：残り時間(まだ15分以上ある場合は、待たない)
        if (target_time - current_time).total_seconds() > 900:
            print(f"too early. return.")
            return

        # 指定した時間まで待機
        while current_time < target_time:
            print(f"Waiting until {target_time.strftime('%H:%M:%S')}...")
            time.sleep(10)  # 10秒ごとに確認

            # 現在の時間を更新
            current_time = datetime.datetime.now()

    def airdrop(self):
        contract = self.web3.eth.contract(address=self.airdropAddr, abi=self.MchvAirdropAbi)
        start = self.startAddressIndex
        end = self.maxAddressIndex
        cnt = end - start + 1

        print(f'{self.LogTime()} airdrop start:{start} end:{end}')

        # 前回処理の終了時間を初期化
        last_processed_time = time.time()

        for i in range(cnt):
            address_index = i + start
            account = self.wallet.GetAddress(address_index)
            privateKey = account.private_key()
            walletAddr = account.p2pkh_address()

            try:
                # 前データとの時間差を計算
                time_difference = time.time() - last_processed_time

                # Intervalの秒経過していない場合は待つ
                if time_difference < self.airdropInterval:
                    time.sleep(self.airdropInterval - time_difference)
 
                # 処理の開始時間
                last_processed_time = time.time()

                # nonce = self.web3.eth.getTransactionCount(walletAddr)
                nonce = self.getNonce(address_index, walletAddr)

                tx_content = {
                    # 'type': '0x2',
                    'nonce': nonce,
                    'chainId': 29548,
                    "from": walletAddr,
                    'gas': 260000,
                    "gasPrice": Web3.toWei(0, "gwei"),
                }
            
                #airdrop関数
                tx = contract.functions.airdrop().buildTransaction(tx_content)

                signed_tx = self.web3.eth.account.sign_transaction(tx, privateKey)
                tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

                # tx結果を待たず送りっぱなしとする
                # result = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                # success = result['status']

                print(f'{self.LogTime()} {address_index}:{walletAddr}')

            except Exception as e:
                print(f'{self.LogTime()} {address_index}:{walletAddr}：{e}')

                # airdrop枯渇したら終了
                if str(e) == "{'code': -32000, 'message': 'execution reverted: COLOSSEUM_AIRDROP_AMOUNT_EXCEEDS_LIMIT'}":
                    print(f"airdrop empty. return.")
                    break

                # DOS対策
                if "Too Many Requests for url" in str(e):
                    print(f"Too Many Requests. waiting...3s")
                    time.sleep(3)

    def transferAll(self):
        mainAccount = self.wallet.GetAddress(0)
        mainAddr = mainAccount.p2pkh_address()
        start = self.startAddressIndex
        end = self.maxAddressIndex
        cnt = end - start + 1

        print(f'{self.LogTime()} transfer start:{start} end:{end}')
        print(f'to:{mainAddr}')

        # 前回処理の終了時間を初期化
        last_processed_time = time.time()

        for i in range(cnt):
            address_index = i + start
            account = self.wallet.GetAddress(address_index)
            privateKey = account.private_key()
            walletAddr = account.p2pkh_address()

            try:
                # 前データとの時間差を計算
                time_difference = time.time() - last_processed_time

                # Intervalの秒経過していない場合は待つ
                if time_difference < self.airdropInterval:
                    time.sleep(self.airdropInterval - time_difference)
 
                # 処理の開始時間
                last_processed_time = time.time()

                balance = self.web3.eth.getBalance(walletAddr)
                if balance == 0: continue
                nonce = self.web3.eth.getTransactionCount(walletAddr)

                tx_content = {
                    'nonce': nonce,
                    # 'chainId': 2400,
                    'chainId': 29548,                    
                    'from': walletAddr,
                    'to': mainAddr,
                    # 'value': Web3.toWei(0, 'ether'),
                    'value': balance,
                    'gas': 21000,
                    "gasPrice": Web3.toWei(0, "gwei"),
                }
    
                signed_tx = self.web3.eth.account.sign_transaction(tx_content, privateKey)
                tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

                # tx結果を待たず送りっぱなしとする
                # result = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                # success = result['status']

                print(f'{self.LogTime()} {address_index}:{walletAddr}:{balance}')

            except Exception as e:
                print(f'{self.LogTime()} {address_index}:{walletAddr}：{e}')
