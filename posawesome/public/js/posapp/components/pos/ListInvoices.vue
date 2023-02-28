<template>
  <v-row justify="center">
    <v-dialog v-model="invoicesListDialog" max-width="800px">
      <!-- <template v-slot:activator="{ on, attrs }">
        <v-btn color="primary" dark v-bind="attrs" v-on="on">Open Dialog</v-btn>
      </template>-->
      <v-card>
        <v-card-title>
          <span class="headline primary--text">{{
            __('Invoices List')
          }}</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>
            <v-row>
              <v-col cols="12" class="pa-1">
                <div class="mx-2 my-5">
                  <v-text-field
                    v-model="search"
                    append-icon="mdi-magnify"
                    :label="__('Search by Part of Invoice Name, Amount or Table Name')"
                    single-line
                    hide-details
                  ></v-text-field>
                </div>
                <template>
                  <v-data-table
                    :headers="headers"
                    :items="invoices_data"
                    item-key="name"
                    class="elevation-1"
                    :single-select="singleSelect"
                    :footer-props="{'items-per-page-options':[5, -1]}"
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
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <v-btn color="success" dark @click="print_invoice">Print</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  // props: ["draftsDialog"],
  data: () => ({
    invoicesListDialog: false,
    singleSelect: true,
    selected: [],
    invoices_data: [],
    search: '',
    headers: [
      {
        text: __('Customer'),
        value: 'customer',
        align: 'start',
        filterable: true,
        sortable: true,
      },
      {
        text: __('Date'),
        align: 'start',
        sortable: true,
        value: 'posting_date',
      },
      {
        text: __('Invoice'),
        value: 'name',
        align: 'start',
        sortable: true,
      },
      {
        text: __('Amount'),
        value: 'grand_total',
        align: 'start',
        sortable: false,
      },
      {
        text: __('Table'),
        value: 'posa_pos_restaurant_table',
        align: 'start',
        sortable: true,
      }
    ],
  }),
  watch: {
    search(value) {
      this.search_invoice(value);
    }
  },
  methods: {
    close_dialog() {
      this.invoicesListDialog = false;
    },

    print_invoice() {
      if (this.selected.length > 0) {

        this.load_print_page(this.selected[0].name)
        // evntBus.$emit('load_invoice', this.selected[0]);
        // this.invoicesListDialog = false;
      }
    },
    load_print_page(invoice_name) {
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=Sales%20Invoice&name=' +
        invoice_name +
        '&trigger_print=1' +
        '&format=' +
        print_format +
        '&no_letterhead=' +
        letter_head;
      const printWindow = window.open(url, 'Print');
      printWindow.addEventListener(
        'load',
        function () {
          printWindow.print();
          // printWindow.close();
          // NOTE : uncomoent this to auto closing printing window
        },
        true
      );
    },
    search_invoice(term) {
      frappe.call(
      {
        method: "posawesome.api.get_invoices_list",
        args: {term: term},
        callback: (r) => {          
          this.invoices_data = r.message;
        }
      })
    }
  },
  created: function () {
    evntBus.$on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    evntBus.$on('open_invoices_list', (data) => {
      this.invoicesListDialog = true;
      this.selected = [];
      this.search_invoice();
    });
    this.search_invoice();
  }
};
</script>
