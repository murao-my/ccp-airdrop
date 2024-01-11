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

        self.startAddressIndex = src.config.startAddressIndex()
        self.maxAddressIndex = src.config.maxAddressIndex()
        self.airdropInterval = src.config.airdropInterval()
        self.wallet_nonces = {}

        chain = "MCHV"
        self.web3 = Web3(Web3.HTTPProvider(src.config.getNetworkURL(chain)))       
        self.isConnected = self.web3.isConnected()
        if self.isConnected == False:
            print('connection fail')
            return

        with open('./abi/MCHV.airdrop.json') as f:
            self.MchvAirdropAbi = json.load(f)

        self.airdropAddr = Web3.toChecksumAddress(src.config.TokenAddress.MCHV_airdropAddr)

    def LogTime(self):
        return datetime.datetime.now()
    
    def keepNonce(self):
        start = self.startAddressIndex
        end = self.maxAddressIndex
        cnt = end - start + 1

        for i in range(cnt):
            address_index = i + start
            account = self.wallet.GetAddress(address_index)
            walletAddr = account.p2pkh_address()

            nonce = self.web3.eth.getTransactionCount(walletAddr)
            self.wallet_nonces[walletAddr] = nonce

    def getNonce(self, walletAddr):
        if walletAddr in self.wallet_nonces:
            return self.wallet_nonces[walletAddr]
        else:
            nonce = self.web3.eth.getTransactionCount(walletAddr)
            return nonce

    def airdropWaiting(self):
        # 待機する時間を設定（6:00）UTC時間
        target_time = datetime.datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)

        # 現在の時間を取得
        current_time = datetime.datetime.now()

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

        # f = open('./logs/airdropAll.log', 'w')
        # f.write(f'airdropAll start:{self.LogTime()}\n')
        # f.write(f'start:{start} end:{end}\n')
        # f.close()
        print(f'airdrop start:{self.LogTime()}\n')
        print(f'start:{start} end:{end}\n')

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
                nonce = self.getNonce(walletAddr)

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

                result = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                success = result['status']

                # f = open('./logs/airdropAll.log', 'a')
                # f.write(f'{self.LogTime()} {address_index}:{walletAddr}:{success}\n')
                # f.close()
                print(f'{self.LogTime()} {address_index}:{walletAddr}:{success}\n')

            except Exception as e:
                print(f'{self.LogTime()} {e}')

                # f = open('./logs/airdropAll.error.log', 'a')
                # f.write(f'{self.LogTime()} {address_index}:{walletAddr}:{privateKey}{e}\n')
                # f.close()

    def transferAll(self):
        mainAccount = self.wallet.GetAddress(0)
        mainAddr = mainAccount.p2pkh_address()
        start = self.startAddressIndex
        end = self.maxAddressIndex
        cnt = end - start + 1

        # f = open('./logs/transferAll.log', 'w')
        # f.write(f'transferAll start:{self.LogTime()}\n')
        # f.write(f'start:{start} end:{end}\n')
        # f.write(f'to:{mainAddr}:{mainAccount.private_key()}\n')
        # f.close()
        print(f'transferAll start:{self.LogTime()}\n')
        print(f'start:{start} end:{end}\n')
        print(f'to:{mainAddr}\n')

        for i in range(cnt):
            time.sleep(1)
            address_index = i + start
            account = self.wallet.GetAddress(address_index)
            privateKey = account.private_key()
            walletAddr = account.p2pkh_address()

            try:
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

                result = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                success = result['status']

                # f = open('./logs/transferAll.log', 'a')
                # f.write(f'{self.LogTime()} {address_index}:{walletAddr}:{success}\n')
                # f.close()
                print(f'{self.LogTime()} {address_index}:{walletAddr}:{balance}\n')

            except Exception as e:
                print(f'{self.LogTime()} {e}')

                # f = open('./logs/transferAll.error.log', 'a')
                # f.write(f'{self.LogTime()} {address_index}:{walletAddr}:{privateKey}{e}\n')
                # f.close()
            
    # def faucetAll(self):
    #     contract = self.web3.eth.contract(address=self.faucetAddr, abi=self.FaucetAbi)
    #     start = self.startAddressIndex
    #     end = self.maxAddressIndex
    #     cnt = end - start + 1

    #     f = open('./logs/faucetAll.log', 'w')
    #     f.write(f'faucetAll start:{self.LogTime()}\n')
    #     f.write(f'start:{start} end:{end}\n')
    #     f.close()

    #     for i in range(cnt):
    #         address_index = i + start
    #         account = self.wallet.GetAddress(address_index)
    #         privateKey = account.private_key()
    #         walletAddr = account.p2pkh_address()

    #         try:
    #             nonce = self.web3.eth.getTransactionCount(walletAddr)

    #             tx_content = {
    #                 # 'type': '0x2',
    #                 'nonce': nonce,
    #                 'chainId': 2400,
    #                 "from": walletAddr,
    #                 'gas': 63000,
    #                 "gasPrice": Web3.toWei(0, "gwei"),
    #             }
            
    #             #request関数
    #             tx = contract.functions.request().buildTransaction(tx_content)

    #             signed_tx = self.web3.eth.account.sign_transaction(tx, privateKey)
    #             tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    #             result = self.web3.eth.wait_for_transaction_receipt(tx_hash)
    #             success = result['status']

    #             f = open('./logs/faucetAll.log', 'a')
    #             f.write(f'{self.LogTime()} {address_index}:{walletAddr}:{success}\n')
    #             f.close()
    #         except Exception as e:
    #             f = open('./logs/faucetAll.error.log', 'a')
    #             f.write(f'{self.LogTime()} {address_index}:{walletAddr}:{privateKey}{e}\n')
    #             f.close()
