<template>
  <div fluid class="mt-2">
    <ClosingDialog></ClosingDialog>
    <Drafts></Drafts>
    <SalesOrders></SalesOrders>
    <Returns></Returns>
    <NewAddress></NewAddress>
    <MpesaPayments></MpesaPayments>
    <Variants></Variants>
    <OpeningDialog v-model:dialog="dialog" />
    <v-row v-show="!dialog">
      <v-col v-show="!payment && !offers && !coupons" xl="6" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <ItemsSelector></ItemsSelector>
      </v-col>
      <v-col v-show="offers" xl="6" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <PosOffers></PosOffers>
      </v-col>
      <v-col v-show="coupons" xl="6" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <PosCoupons></PosCoupons>
      </v-col>
      <v-col v-show="payment" xl="6" lg="6" md="6" sm="6" cols="12" class="pos pr-0">
        <Payments></Payments>
      </v-col>

      <v-col xl="6" lg="6" md="6" sm="6" cols="12" class="pos">
        <Invoice></Invoice>
      </v-col>
    </v-row>
    <warehouse-dialog
      v-if="showWarehouseDialog"
      :item="selectedItem"
      :warehouses="pos_plus_additional_warehouses"
      :main_warehouse="main_warehouse"
      @select="handleWarehouseSelect"
      @close="showWarehouseDialog = false"
    />
    <item-information-dialog
      v-if="showItemInformationDialog"
      :item="selectedItem"
      :warehouses="pos_plus_additional_warehouses"
      :main_warehouse="main_warehouse"
      @select="handleWarehouseSelect"
      @close="showItemInformationDialog = false"
    />
    <offer-dialog
      v-if="showOffersDialog"
      :key="offersDialogArgs.item_code + '-' + offersDialogArgs.warehouse + '-' + Date.now()"
      :item-code="offersDialogArgs.item_code"
      :warehouse="offersDialogArgs.warehouse"
      :pos_profile="pos_profile_name"
      @close="showOffersDialog = false"
    />
  </div>
</template>

<script>

import ItemsSelector from "./ItemsSelector.vue";
import Invoice from "./Invoice.vue";
import OpeningDialog from "./OpeningDialog.vue";
import Payments from "./Payments.vue";
import PosOffers from "./PosOffers.vue";
import PosCoupons from "./PosCoupons.vue";
import Drafts from "./Drafts.vue";
import SalesOrders from "./SalesOrders.vue";
import ClosingDialog from "./ClosingDialog.vue";
import NewAddress from "./NewAddress.vue";
import Variants from "./Variants.vue";
import Returns from "./Returns.vue";
import MpesaPayments from "./Mpesa-Payments.vue";
import WarehouseDialog from './WarehouseDialog.vue';
import ItemInformationDialog from './ItemInformationDialog.vue';
import OfferDialog from './OfferDialog.vue';

export default {
  data: function () {
    return {
      dialog: false,
      pos_profile: "",
      pos_opening_shift: "",
      payment: false,
      offers: false,
      coupons: false,
      showWarehouseDialog: false,
      showItemInformationDialog: false,
      selectedItem: null,
      pos_plus_additional_warehouses: [],
      main_warehouse: "",
      showOffersDialog: false,
      offersDialogArgs: null,
      pos_profile_name: "",
    };
  },

  components: {
    ItemsSelector,
    Invoice,
    OpeningDialog,
    Payments,
    Drafts,
    ClosingDialog,

    Returns,
    PosOffers,
    PosCoupons,
    NewAddress,
    Variants,
    MpesaPayments,
    WarehouseDialog,
    ItemInformationDialog,
    OfferDialog,
    SalesOrders,
  },

  created() {
    this.eventBus.on('show_warehouse_dialog', (item) => {
      this.selectedItem = item;
      this.showWarehouseDialog = true;
    });
    this.eventBus.on('show_item_details_dialog', (item) => {
      this.selectedItem = item;
      this.showItemInformationDialog = true;
    });
    this.eventBus.on('show_offers_dialog', (args) => {
      this.offersDialogArgs = args;
      this.showOffersDialog = true;
    });
  },

  methods: {
    handleWarehouseSelect(itemWithWarehouse) {
      this.eventBus.emit('add_item', itemWithWarehouse);
    },
    check_opening_entry() {
      return frappe
        .call("posawesome.posawesome.api.posapp.check_opening_shift", {
          user: frappe.session.user,
        })
        .then((r) => {
          if (r.message) {
            this.pos_profile = r.message.pos_profile;
            this.pos_profile_name = r.message.pos_profile.name;
            this.pos_plus_additional_warehouses =  r.message.pos_profile.pos_plus_additional_warehouses;
            this.main_warehouse =  r.message.pos_profile.warehouse;
            this.pos_opening_shift = r.message.pos_opening_shift;
            this.get_offers(this.pos_profile.name);
            this.eventBus.emit('register_pos_profile', r.message);
            this.eventBus.emit('set_company', r.message.company);
            frappe.realtime.emit('pos_profile_registered');
            console.info("LoadPosProfile");
          } else {
            this.create_opening_voucher();
          }
        });
    },
    create_opening_voucher() {
      this.dialog = true;
    },
    get_closing_data() {
      return frappe
        .call(
          "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening",
          {
            opening_shift: this.pos_opening_shift,
          }
        )
        .then((r) => {
          if (r.message) {
            this.eventBus.emit("open_ClosingDialog", r.message);
          } else {
            // console.log(r);
          }
        });
    },
    submit_closing_pos(data) {
      frappe
        .call(
          "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift",
          {
            closing_shift: data,
          }
        )
        .then((r) => {
          if (r.message) {
            this.eventBus.emit('show_message', {
              title: `POS Shift Closed`,
              color: "success",
            });
            this.check_opening_entry();
          } else {
            console.log(r);
          }
        });
    },
    get_offers(pos_profile) {
      return frappe
        .call("posawesome.posawesome.api.posapp.get_offers", {
          profile: pos_profile,
        })
        .then((r) => {
          if (r.message) {
            console.info("LoadOffers");
            this.eventBus.emit("set_offers", r.message);
          }
        });
    },
    get_pos_setting() {
      frappe.db.get_doc("POS Settings", undefined).then((doc) => {
        this.eventBus.emit("set_pos_settings", doc);
      });
    },
  },

  mounted: function () {
    this.$nextTick(function () {
      this.check_opening_entry();
      this.get_pos_setting();
      this.eventBus.on("close_opening_dialog", () => {
        this.dialog = false;
      });
      this.eventBus.on("register_pos_data", (data) => {
        try {
          this.pos_profile = data.pos_profile;
          this.get_offers(this.pos_profile.name);
          this.pos_opening_shift = data.pos_opening_shift;
          this.eventBus.emit("register_pos_profile", data);
          console.info("LoadPosProfile");
        }
        catch(e) {
          console.error('error in register_pos_data', e);
        }
      });
      this.eventBus.on("show_payment", (data) => {
        this.payment = true ? data === "true" : false;
        this.offers = false ? data === "true" : false;
        this.coupons = false ? data === "true" : false;
      });
      this.eventBus.on("show_offers", (data) => {
        this.offers = true ? data === "true" : false;
        this.payment = false ? data === "true" : false;
        this.coupons = false ? data === "true" : false;
      });
      this.eventBus.on("show_coupons", (data) => {
        this.coupons = true ? data === "true" : false;
        this.offers = false ? data === "true" : false;
        this.payment = false ? data === "true" : false;
      });
      this.eventBus.on("open_closing_dialog", () => {
        this.get_closing_data();
      });
      this.eventBus.on("submit_closing_pos", (data) => {
        this.submit_closing_pos(data);
      });
    });
  },
  beforeUnmount() {
    this.eventBus.off("close_opening_dialog");
    this.eventBus.off("register_pos_data");
    this.eventBus.off("LoadPosProfile");
    this.eventBus.off("show_offers");
    this.eventBus.off("show_coupons");
    this.eventBus.off("open_closing_dialog");
    this.eventBus.off("submit_closing_pos");
    this.eventBus.off('show_offers_dialog');
  },
};
</script>

<style scoped></style>
