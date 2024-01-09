from hdwallet import HDWallet
from hdwallet.utils import generate_mnemonic, is_mnemonic
from hdwallet.symbols import ETH

class MyHDWallet():

    def __init__(self):
        mnemonic = ""

    def Generatenemonic(self):
        # Choose strength 128, 160, 192, 224 or 256
        strength: int = 128  # Default is 128
        # Choose language english, french, italian, spanish, chinese_simplified, chinese_traditional, japanese or korean
        lang = "english"  # Default is english

        mnemonic_e = generate_mnemonic(language=lang, strength=strength)
        print("----------------------------------")
        print("generate mnemonic phrase: {}".format(mnemonic_e))
        print("----------------------------------")
        self.SetMnemonic(mnemonic_e)

    def SetMnemonic(self, mnemonic):
        if is_mnemonic(mnemonic) == False:
            print("error mnemonic phrase")
            return

        self.mnemonic = mnemonic
        self.hd_wallet = HDWallet(symbol=ETH).from_mnemonic(mnemonic=self.mnemonic)

    def GetAddress(self, address_index):
        # 0:BTC, 60:ETH, 966:MATIC
        coin_type = "60"

        self.hd_wallet.clean_derivation()
        wallet_hdpath = "m/44'/{0}'/0'/0/{1}".format(coin_type, str(address_index))
        return self.hd_wallet.from_path(path=wallet_hdpath)
