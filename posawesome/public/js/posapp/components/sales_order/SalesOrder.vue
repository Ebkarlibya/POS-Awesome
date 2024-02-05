<template>
  <div fluid>
    <v-row v-show="!dialog">
      <v-col md="8" cols="12" class="pb-2 pr-0">
        <v-card
          class="main mx-auto grey lighten-5 mt-3 p-3 pb-16 overflow-y-auto"
          style="max-height: 94vh; height: 94vh"
        >
          <div>
            <v-row>
              <v-col md="7" cols="12">
                <h3 style="margin-top: 10px">
                  <strong>{{ __("Sales Order List") }}</strong>
                </h3>
                <v-divider></v-divider>
              </v-col>
            </v-row>
            <v-row>
              <v-col md="6" cols="12">
                <div class="mx-2 my-5">
                  <v-text-field
                    v-model="search"
                    append-icon="mdi-magnify"
                    :label="
                      __('Search by Part of Order Name, Amount or Table Name')
                    "
                    single-line
                    hide-details
                  ></v-text-field>
                </div>
              </v-col>
              <v-col md="2" cols="12">
                <v-checkbox
                  v-model="includeDrafts"
                  label="Include Drafts"
                  color="success"
                  :value="!includeDrafts"
                  hide-details
                ></v-checkbox>
              </v-col>
              <v-col md="4" cols="12">
                <v-btn block color="warning" @click="get_list_of_orders" dark>{{
                  __("Search")
                }}</v-btn>
              </v-col>
            </v-row>
            <v-divider></v-divider>
            <v-data-table
              :headers="order_headers"
              :items="orders_data"
              item-key="name"
              class="elevation-1 mt-0"
              show-select
              v-model="selected_orders"
              :loading="order_loading"
              checkbox-color="primary"
              :single-select="true"
            >
              <!-- @item-selected="onOrderSelected" -->
              <template v-slot:item.grand_total="{ item }">
                {{ currencySymbol(item.currency) }}
                {{ formtCurrency(item.grand_total) }}
              </template>
              <template v-slot:item.outstanding_amount="{ item }">
                <span class="primary--text"
                  >{{ currencySymbol(item.currency) }}
                  {{ formtCurrency(item.outstanding_amount) }}</span
                >
              </template>
            </v-data-table>
            <v-divider></v-divider>
          </div>
        </v-card>
      </v-col>

      <!-- Side Panel for info -->
      <v-col md="4" cols="12" class="pb-2 pr-0">
        <v-card
          class="invoices mx-auto grey lighten-5 mt-3 p-3"
          style="max-height: 94vh; height: 94vh"
        >
          <h3 style="margin: 10px">Sales Order Details</h3>
          <v-divider></v-divider>
          <template v-if="selected_orders.length != 0">
            <h4 class="primary--text">Totals</h4>
            <v-row class="mx-2 my-5">
              <v-col md="8" cols="12">Grand Total</v-col>
              <v-col md="4" cols="12">
                <v-text-field
                  class="p-0 m-0"
                  dense
                  color="primary"
                  background-color="white"
                  hide-details
                  :value="selected_orders[0].grand_total"
                  readonly
                  flat
                  :prefix="currencySymbol(pos_profile_details.currency)"
                ></v-text-field>
                {{
              }}</v-col>
            </v-row>
            <v-row>
              <v-divider></v-divider>
              <v-data-table
                :headers="order_items_headers"
                :items="selected_order_items"
                item-key="name"
                class="elevation-1 mt-0"
                :loading="order_loading"
                checkbox-color="primary"
              >
              </v-data-table>
            </v-row>
            <div
              class="pb-6 pr-6"
              style="position: absolute; bottom: 0; width: 100%"
            >
              <v-btn block color="primary" dark @click="print_invoice">
                {{ __("Print") }}
              </v-btn>
            </div>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import format from "../../format";
import Customer from "../pos/Customer.vue";
import UpdateCustomer from "../pos/UpdateCustomer.vue";
import { evntBus } from "../../bus";

export default {
  mixins: [format],
  components: { Customer, UpdateCustomer },
  data: function () {
    return {
      dialog: false,
      pos_profile: "",
      pos_profile_details: {},

      orders_data: [],
      includeDrafts: false,
      search: "",
      orders_loading: false,
      selected_orders: [],
      order_loading: false,
      order_headers: [
        {
          text: __("Order Name"),
          align: "start",
          sortable: true,
          value: "name",
        },
        {
          text: __("Customer"),
          align: "start",
          sortable: true,
          value: "customer",
        },
        {
          text: __("Date"),
          align: "start",
          sortable: true,
          value: "transaction_date",
        },
        {
          text: __("Due Date"),
          align: "start",
          sortable: true,
          value: "delivery_date",
        },
        {
          text: __("Total"),
          align: "end",
          sortable: true,
          value: "grand_total",
        },
        {
          text: __("Status"),
          align: "end",
          sortable: true,
          value: "status",
        },
      ],

      selected_order_items: [],
      order_items_headers: [
        {
          text: __("Item Name"),
          align: "start",
          sortable: true,
          value: "item_code",
        },
        {
          text: __("Qty"),
          align: "start",
          sortable: true,
          value: "qty",
        },
        {
          text: __("Rate"),
          align: "end",
          sortable: true,
          value: "rate",
        },
        {
          text: __("Amount"),
          align: "end",
          sortable: true,
          value: "amount",
        },
      ],
    };
  },
  methods: {
    get_list_of_orders() {
      this.orders_loading = true;
      return frappe.call({
        method: "posawesome.posawesome.api.order.get_orders_list",
        args: { term: this.search.trim(), include_drafts: this.includeDrafts },
        callback: (r) => {
          if (r.message) {
            this.orders_data = r.message.map((el) => {
              el.status = `(${el.docstatus === 0 ? "Draft" : "Submitted"})`;
              return el;
            });
          } else {
            console.log("error");
          }

          this.orders_loading = false;
        },
      });
    },

    get_order_items() {
      return frappe.call({
        method: "posawesome.posawesome.api.order.get_order_items",
        args: { order: this.selected_orders[0] },
        callback: (r) => {
          if (r.message) {
            this.selected_order_items = r.message.map((el) => {
              el.rate = `${el.rate}  ${this.pos_profile_details.currency}`;
              el.amount = `${el.amount} ${this.pos_profile_details.currency}`;
              return el;
            });
          }
        },
      });
    },

    check_opening_entry() {
      return frappe
        .call("posawesome.posawesome.api.posapp.check_opening_shift", {
          user: frappe.session.user,
        })
        .then((r) => {
          if (r.message) {
            this.pos_profile_details = r.message.pos_profile;
            this.pos_profile = r.message.pos_profile.name;
            //   this.pos_opening_shift = r.message.pos_opening_shift;
            //   this.get_offers(this.pos_profile.name);
            //   evntBus.$emit("register_pos_profile", r.message);
            //   evntBus.$emit("set_company", r.message.company);
            //   console.info("LoadPosProfile");
            // } else {
            //   this.create_opening_voucher();
          }
        });
    },
    print_invoice() {
      this.load_print_page(this.selected_orders[0].name);
      // evntBus.$emit('load_invoice', this.selected[0]);
      // this.invoicesListDialog = false;
    },
    load_print_page(order_name) {
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        "/printview?doctype=Sales%20Order&name=" +
        order_name +
        "&trigger_print=1" +
        "&format=" +
        print_format +
        "&no_letterhead=" +
        letter_head;
      const printWindow = window.open(url, "Print");
      printWindow.addEventListener(
        "load",
        function () {
          printWindow.print();
          // printWindow.close();
          // NOTE : uncomoent this to auto closing printing window
        },
        true
      );
    },
  },

  watch: {
    selected_orders(value, old) {
      this.get_order_items();
    },
    includeDrafts() {
      this.get_list_of_orders();
    },
  },

  mounted: function () {
    this.$nextTick(function () {
      this.check_opening_entry();
      this.get_list_of_orders();
    });
  },
};
</script>

<style>
input[total_of_diff] {
  text-align: right;
}
input[payments_methods] {
  text-align: right;
}
input[total_selected_payments] {
  text-align: right;
}
input[total_selected_invoices] {
  text-align: right;
}
input[total_selected_mpesa_payments] {
  text-align: right;
}
</style>
