<template>
  <v-row justify="center">
    <v-dialog v-model="ordersListDialog" max-width="800px">
      <!-- <template v-slot:activator="{ on, attrs }">
          <v-btn color="primary" dark v-bind="attrs" v-on="on">Open Dialog</v-btn>
        </template>-->
      <v-card>
        <v-card-title>
          <span class="headline primary--text">{{ __("Orders List") }}</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>
            <v-row>
              <v-col cols="12" class="pa-1">
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
                <template>
                  <!-- <v-container>
                      <v-checkbox v-model="includeDrafts" :label="__('Include Drafts')"></v-checkbox>
                    </v-container> -->
                  <v-data-table
                    :headers="headers"
                    :items="orders_data"
                    item-key="name"
                    class="elevation-1"
                    :single-select="singleSelect"
                    :footer-props="{ 'items-per-page-options': [5, -1] }"
                    show-select
                    v-model="selected"
                  >
                  </v-data-table>
                </template>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">{{
            __("Close")
          }}</v-btn>
          <v-btn color="success" dark @click="print_invoice">{{
            __("Print")
          }}</v-btn>
          <!-- <v-btn
            color="secondary"
            v-if="
              pos_profile.posa_enable_warranty_print_system &&
              this.selected[0] &&
              this.selected[0].posa_has_warranty === 'Yes'
            "
            dark
            @click="print_warranty_invoice"
            >{{ __("Print Warranty") }}</v-btn
          > -->
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from "../../bus";
export default {
  // props: ["draftsDialog"],
  data: () => ({
    ordersListDialog: false,
    singleSelect: true,
    includeDrafts: false,
    selected: [],
    orders_data: [],
    search: "",
    headers: [
      {
        text: __("Customer"),
        value: "customer",
        align: "start",
        filterable: true,
        sortable: true,
      },
      {
        text: __("Date"),
        align: "start",
        sortable: true,
        value: "delivery_date",
      },
      // {
      //   text: __('Status'),
      //   align: 'start',
      //   sortable: true,
      //   value: 'status',
      // },
      {
        text: __("Order"),
        value: "name",
        align: "start",
        sortable: true,
      },
      {
        text: __("Amount"),
        value: "grand_total",
        align: "start",
        sortable: false,
      },
    ],
  }),
  watch: {
    search(value) {
      this.search_order(value);
    },
    includeDrafts(value) {
      this.search_order(value);
    },
  },
  methods: {
    close_dialog() {
      this.ordersListDialog = false;
    },

    print_invoice() {
      if (this.selected.length > 0) {
        this.load_print_page(this.selected[0].name);
        // evntBus.$emit('load_invoice', this.selected[0]);
        // this.invoicesListDialog = false;
      }
    },
    // print_warranty_invoice() {
    //   if (
    //     this.selected.length > 0 &&
    //     this.selected[0].posa_has_warranty === "Yes"
    //   ) {
    //     this.load_warranty_print_page(this.selected[0].name);
    //     // evntBus.$emit('load_invoice', this.selected[0]);
    //     // this.invoicesListDialog = false;
    //   }
    // },
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
    // load_warranty_print_page(order_name) {
    //   const letter_head = this.pos_profile.letter_head || 0;
    //   const url =
    //     frappe.urllib.get_base_url() +
    //     "/printview?doctype=Sales%20Order&name=" +
    //     order_name +
    //     "&trigger_print=1" +
    //     "&format=" +
    //     this.pos_profile.posa_warranty_print_format +
    //     "&no_letterhead=" +
    //     letter_head;
    //   const printWindow = window.open(url, "PrintWarranty");
    //   printWindow.addEventListener(
    //     "load",
    //     function () {
    //       printWindow.print();
    //       // printWindow.close();
    //     },
    //     true
    //   );
    // },
    search_order() {
      frappe.call({
        method: "posawesome.posawesome.api.order.get_orders_list",
        args: { term: this.search.trim(), include_drafts: this.includeDrafts },
        callback: (r) => {
          // this.invoices_data = r.message.map(el => {
          //   el.status = `(${el.docstatus === 0 ? 'Draft' : 'Submitted'})`
          //   return el
          // });
          this.orders_data = r.message;
        },
      });
    },
  },
  created: function () {
    evntBus.$on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;

      if (this.pos_profile.posa_enable_pos_restaurant_table) {
        this.headers.push({
          text: __("Table"),
          value: "posa_pos_restaurant_table",
          align: "start",
          sortable: true,
        });
      }
      if (this.pos_profile.posa_enable_warranty_print_system) {
        this.headers.push({
          text: __("Has Warranty"),
          value: "posa_has_warranty",
          align: "start",
          sortable: true,
        });
      }
    });
    evntBus.$on("open_orders_list", (data) => {
      this.ordersListDialog = true;
      this.selected = [];
      this.search_order();
    });
    this.search_order();
  },
};
</script>
