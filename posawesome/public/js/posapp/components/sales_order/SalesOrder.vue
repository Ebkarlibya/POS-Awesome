<template>
  <v-container fluid>
    <v-row v-show="!dialog">
      <v-col md="8" cols="12" class="pb-2 pr-0">
        <v-card
          class="main mx-auto bg-grey-lighten-5 mt-3 p-3 pb-16 overflow-y-auto"
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
              <v-col md="7" cols="12">
                <v-text-field
                  v-model="search"
                  append-icon="mdi-magnify"
                  :label="
                    __('Search by Part of Order Name, Amount or Table Name')
                  "
                  single-line
                  hide-details
                  @keyup.enter="get_list_of_orders"
                  clearable
                  @click:clear="search = ''; get_list_of_orders()"
                  clear-icon="mdi-close-circle-outline"
                ></v-text-field>
              </v-col>
              <v-col md="2" cols="12">
                <v-checkbox
                  v-model="includeDrafts"
                  label="Include Drafts"
                  color="success"
                  hide-details
                ></v-checkbox>
              </v-col>
              <v-col md="3" cols="12">
                <v-btn
                  block
                  color="warning"
                  @click="get_list_of_orders"
                  dark
                >
                  {{ __("Search") }}
                </v-btn>
              </v-col>
            </v-row>
            <v-divider></v-divider>
            <v-data-table
              :headers="order_headers"
              :items="orders_data"
              item-value="name"
              return-object
              class="elevation-1 mt-0"
              show-select
              v-model="selected_orders"
              :loading="orders_loading"
              select-strategy="single"
            >
              <template #item.grand_total="{ item }">
                {{ currencySymbol(item.currency) }}
                {{ formatCurrency(item.grand_total) }}
              </template>
              <template #item.status="{ item }">
                <v-chip variant="elevated" :color="item.color">
                  {{ item.status }}
                </v-chip>
              </template>
            </v-data-table>
            <v-divider></v-divider>
          </div>
        </v-card>
      </v-col>

      <!-- Side Panel for info -->
      <v-col
        md="4"
        cols="12"
        class="pb-2 pr-0"
        v-if="selected_orders.length != 0"
      >
        <v-card
          class="invoices mx-auto grey lighten-5 mt-3 p-3"
          style="max-height: 94vh; height: 94vh"
        >
          <h3 style="margin: 10px">Sales Order Details</h3>
          <v-divider></v-divider>
          <template v-if="selected_orders.length != 0">
            <h4 class="text-primary"> {{ selected_orders[0].name }} </h4>
            <h4 class="text-primary"> {{ __("Totals:") }} </h4>
            <v-row class="mx-2 my-5">
              <v-col md="8" cols="12">{{ __("Grand Total") }}</v-col>
              <v-col md="4" cols="12">
                <v-text-field
                  class="p-0 m-0"
                  density="compact"
                  color="primary"
                  bg-color="white"
                  hide-details
                  v-model="selected_orders[0].grand_total"
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
                item-value="name"
                class="elevation-1 mt-0"
                :loading="order_loading"
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
  </v-container>
</template>

<script>
import format from "../../format";

export default {
  mixins: [format],
  data: function () {
    return {
      dialog: false,
      pos_profile: "",
      pos_profile_details: {},
      orders_data: [],
      includeDrafts: false,
      search: "",
      selected_orders: [],
      orders_loading: false,
      order_loading: false,
      order_headers: [
        {
          title: __("Order Name"),
          align: "start",
          sortable: true,
          key: "name",
        },
        {
          title: __("Customer"),
          align: "start",
          sortable: true,
          key: "customer",
        },
        {
          title: __("Date"),
          align: "start",
          sortable: true,
          key: "transaction_date",
        },
        {
          title: __("Due Date"),
          align: "start",
          sortable: true,
          key: "delivery_date",
        },
        {
          title: __("Total"),
          align: "start",
          sortable: true,
          key: "grand_total",
        },
        {
          title: __("Status"),
          align: "start",
          sortable: true,
          key: "status",
        },
      ],

      selected_order_items: [],
      order_items_headers: [
        {
          title: __("Item Name"),
          align: "start",
          sortable: true,
          key: "item_code",
        },
        {
          title: __("Qty"),
          align: "start",
          sortable: true,
          key: "qty",
        },
        {
          title: __("Rate"),
          align: "start",
          sortable: true,
          key: "rate",
        },
        {
          title: __("Amount"),
          align: "start",
          sortable: true,
          key: "amount",
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
              el.color = ["Cancelled", "Closed"].includes(el.status)
                ? "red"
                : el.status === "Completed"
                ? "green"
                : "yellow";

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
      this.order_loading = true;
      
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

          this.order_loading = false;
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
            //   this.get_offers(this.pos_profile_details.name);
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
        this.pos_profile_details.print_format_for_online ||
        this.pos_profile_details.print_format;
      const letter_head = this.pos_profile_details.letter_head || 0;
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
