<template>
  <div class="extra-filters-main">


    <v-dialog v-model="codeScannerDialog" width="600">
      <v-card elevation="2" outlined shaped>
        <v-card-title>{{ __("Barcode & QRCode Scanner") }}
          <v-spacer></v-spacer>
          <v-card-actions>
            <v-btn color="error" @click="closeQRScanner">{{
              __("Close")
            }}</v-btn>
          </v-card-actions>
        </v-card-title>


        <v-card-text>
          <p>{{ codeData }}</p>
          <video id="code_scanner_video_elem" style="width: 100%; max-height: 20%;"></video>
        </v-card-text>

      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import { BrowserMultiFormatReader, NotFoundException } from "@zxing/library"

export default {
  data: () => ({
    codeScannerDialog: false,
    codeData: "",
    codeReader: null
  }),
  methods: {
    async codeScan() {
      try {

        let selectedDeviceId;
        if (!this.codeReader) {
          this.codeReader = new BrowserMultiFormatReader()
        }
        this.codeReader.listVideoInputDevices()
          .then((videoInputDevices) => {
            if (videoInputDevices[1]) {
              selectedDeviceId = videoInputDevices[1].deviceId

            } else {
              selectedDeviceId = videoInputDevices[0].deviceId
            }
            if (videoInputDevices.length >= 1) {
              videoInputDevices.forEach((el) => {
                console.log('videoInputDevices: ', el);
              })

            }

            this.codeReader.decodeFromVideoDevice(selectedDeviceId, 'code_scanner_video_elem', (result, err) => {
              if (result) {
                this.codeData = result.text
                this.$emit("code-data", this.codeData)
                let beep = new Audio("/assets/posawesome/sound/barcode-scanner-beep-sound.mp3")
                beep.play()
                this.codeReader.reset()
                setTimeout(() => {
                  this.closeQRScanner()
                }, 800)
              }
              if (err && !(err instanceof NotFoundException)) {
                console.error(err)
              }
            })
            console.log(`Started continous decode from camera with id ${selectedDeviceId}`)
          })
          .catch((err) => {
            console.error(err)
          })

      } catch (e) {
        alert(e)
      }
    },
    openQRScanner() {
      this.codeScannerDialog = true;
      setTimeout(() => this.codeScan(), 1000)
    },
    closeQRScanner() {
      this.codeScannerDialog = false;
    },
  },
  created: function () {
    this.$nextTick(function () {
      evntBus.$on('open_code_scanner', () => {
        this.openQRScanner();
      });
    });
  }
};
</script>