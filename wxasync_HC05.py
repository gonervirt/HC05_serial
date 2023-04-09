import wx
import asyncio
import wxasync
from bleak import BleakClient,  BleakGATTCharacteristic, BleakScanner, BleakError
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import time
import pyttsx3

#ESP32 serial ble
#MODEL_NBR_UUID="0000181a-0000-1000-8000-00805f9b34fb"
#HC05
MODEL_NBR_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHAR_NBR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"


def parle (chaine):
    engine.say(chaine)
    engine.runAndWait()


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Bluetooth BLE Serial', size=(400, 300))
        
        #cree la fenetre au centre de l'ecran
        self.Centre()
        self.panel = wx.Panel(self)
        
        #couleur et taille
        self.font = wx.Font(45, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.panel.SetForegroundColour((0,0,0))
        self.panel.SetBackgroundColour((255,255,255))
        self.panel.SetFont(self.font)
        
        self.mesure_label = wx.StaticText(self.panel,label="")        
        self.mesure_valeur = wx.StaticText(self.panel, style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE,label="")
        
        #self.text_ctrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.mesure_label, 0, wx.EXPAND, 5)
        self.sizer.Add(self.mesure_valeur, 1, wx.EXPAND, 5)
        
        #self.sizer.Add(self.text_ctrl, 1, wx.EXPAND)
        self.panel.SetSizer(self.sizer)
        
        self.connected=False
        

    
    #Windows closing handler
    def on_close(self, event):
        #asyncio.create_task(self.ble.disconnect_async())
        #event.Skip()
        # cancelling all tasks effectively ends the program
        print("on close event called")
        for task in asyncio.all_tasks():
            task.cancel()


    async def main_loop(self):
        """
        await self.ble.connect_async()
        await asyncio.gather(
            self.read_from_ble(),
            wxasync.AsyncBind(wx.EVT_CLOSE, self.on_close),
        )
        """
        def filter_bluetooth_device(device: BLEDevice, adv: AdvertisementData):
            # This assumes that the device includes the UART service UUID in the
            # advertising data. This test may need to be adjusted depending on the
            # actual advertising data supplied by the device.
            if MODEL_NBR_UUID.lower() in adv.service_uuids:
            #if MODEL_NBR_UUID in adv.service_uuids:
                return True
            return False
        
        #Disconnect Handler
        async def handle_disconnect(_: BleakClient):
            print("Device was disconnected, goodbye.")
            """
            self.mesure_valeur.SetLabel("Connecting")
            parle("en attente de connexion")
            while self.device is None:
                #self.mesure_valeur.AppendText(".")
                self.device = await BleakScanner.find_device_by_filter(filter_bluetooth_device)
            # cancelling all tasks effectively ends the program
            #for task in asyncio.all_tasks():
                #task.cancel()
            """
        
    
        #Receiving data from Bluetooth Handler
        def handle_rx(_: BleakGATTCharacteristic, data: bytearray):
            print("received:", data.decode())
            self.mesure_label.SetLabel("Selecteur: Volts")
            self.mesure_valeur.SetLabel(data.decode())
            parle(data.decode())
           
        while True:   
            #wait for connexion
            self.device = None
            self.mesure_valeur.SetLabel("Connecting")
            parle("en attente de connexion")
            while self.device is None:
                #self.mesure_valeur.AppendText(".")
                self.device = await BleakScanner.find_device_by_filter(filter_bluetooth_device)

            #Device connected
            self.mesure_valeur.SetLabel("Connected")
            parle("Connecté")
            print ('device found')
            time.sleep(2)
            
            # Waiting for data loop
            async with BleakClient(self.device, disconnected_callback=handle_disconnect) as client:
                self.mesure_valeur.SetLabel("En attente de données")
                parle("En attente de données")
                #loop = asyncio.get_running_loop()
                await client.start_notify(CHAR_NBR_UUID, handle_rx)
                #wxasync.AsyncBind(wx.EVT_CLOSE, self.on_close,self)
                self.connected = await client.is_connected()
                while self.connected:
                    #print ('start notify')
                    await asyncio.sleep(1.0)
                    self.connected = await client.is_connected()
                #print ('sortie de boucle')
                #await client.stop_notify(CHAR_NBR_UUID)
                    #print ('end notify')
                    
            parle("Multimètre déconnecté   ")
            print ('sortie de boucle')
            
        """
        await asyncio.gather(
            self.read_from_ble(),
            wxasync.AsyncBind(wx.EVT_CLOSE, self.on_close),
        )
        """


if __name__ == '__main__':
    engine = pyttsx3.init()
    engine.setProperty("rate", 178)
    app = wxasync.WxAsyncApp()
    frame = MyFrame()
    frame.Show()
    loop = asyncio.get_event_loop()
    loop.create_task(frame.main_loop())
    loop.run_until_complete(app.MainLoop())