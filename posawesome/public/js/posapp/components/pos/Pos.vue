<template>
  <div fluid class="mt-2">
    <ClosingDialog></ClosingDialog>
    <Drafts></Drafts>
    <SalesOrders></SalesOrders>
    <Returns></Returns>
    <NewAddress></NewAddress>
    <MpesaPayments></MpesaPayments>
    <Variants
      :invoice_type="invoiceType"
      :pos_profile="pos_profile"
      :selected_currency="selected_currency"
      :exchange_rate="exchange_rate"
    ></Variants>
    <OpeningDialog v-model:dialog="dialog" />
    <v-row v-show="!dialog" class="flex-wrap flex-lg-nowrap" style="min-height: calc(100vh - 40px)">
      <v-col cols="12" lg="6" class="d-flex flex-column pa-0">
        <div v-show="!payment && !offers && !coupons">
          <ItemsSelector />
        </div>

        <PosOffers v-show="offers"></PosOffers>
        <PosCoupons v-show="coupons"></PosCoupons>
        <Payments v-show="payment"></Payments>
      </v-col>

      <v-col cols="12" lg="6" class="d-flex flex-column pa-0">
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
      :pos_profile="pos_profile"
      :selected_currency="selected_currency"
      :exchange_rate="exchange_rate"
    />
    <item-information-dialog
      v-if="showItemInformationDialog"
      :item="selectedItem"
      :warehouses="pos_plus_additional_warehouses"
      :main_warehouse="main_warehouse"
      @select="handleWarehouseSelect"
      @close="showItemInformationDialog = false"
      :pos_profile="pos_profile"
      :selected_currency="selected_currency"
      :exchange_rate="exchange_rate"
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
      invoiceType: "Invoice",
      selected_currency: "",
      exchange_rate: 1,
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
    this.eventBus.on('set_order_type_for_variants', (args) => {
      this.invoiceType = args;
    });
    this.eventBus.on('set_selected_currency_and_exchange_rate_for_variants', (args) => {
      this.selected_currency = args.selected_currency;
      this.exchange_rate = args.exchange_rate;
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
            this.invoiceType = this.pos_profile.posa_default_sales_order ? "Order" : "Invoice"
            this.selected_currency = this.pos_profile.currency;
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
        const show = data === true || data === "true";
        this.payment = show;
        this.offers = false;
        this.coupons = false;
      });
      this.eventBus.on("show_offers", (data) => {
        const show = data === true || data === "true";
        this.offers = show;
        this.payment = false;
        this.coupons = false;
      });
      this.eventBus.on("show_coupons", (data) => {
        const show = data === true || data === "true";
        if (show) this.eventBus.emit('refresh_customer');
        this.coupons = show;
        this.offers = false;
        this.payment = false;
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
    this.eventBus.off('set_order_type_for_variants');
    this.eventBus.off('set_selected_currency_and_exchange_rate_for_variants');
  },
};
</script>

<style scoped>
.col {
  padding: 4px !important;
}

@media (max-width: 1263px) {
  .row {
    gap: 8px;
  }
}
</style>
