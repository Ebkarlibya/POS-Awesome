<template>
  <div>
    <v-autocomplete
      dense
      clearable
      auto-select-first
      outlined
      color="primary"
      :label="frappe._('Customer')"
      v-model="customer"
      :items="customers"
      item-text="customer_name"
      item-value="name"
      background-color="white"
      :no-data-text="__('Customer not found')"
      hide-details
      :filter="customFilter"
      :disabled="readonly"
      append-icon="mdi-plus"
      @click:append="new_customer"
      prepend-inner-icon="mdi-account-edit"
      @click:prepend-inner="edit_customer"
    >
      <template v-slot:item="data">
        <template>
          <v-list-item-content>
            <v-list-item-title
              class="primary--text subtitle-1"
              v-html="data.item.customer_name"
            ></v-list-item-title>
            <v-list-item-subtitle
              v-if="data.item.customer_name != data.item.name"
              v-html="`ID: ${data.item.name}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.tax_id"
              v-html="`TAX ID: ${data.item.tax_id}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.email_id"
              v-html="`Email: ${data.item.email_id}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.mobile_no"
              v-html="`Mobile No: ${data.item.mobile_no}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.primary_address"
              v-html="`Primary Address: ${data.item.primary_address}`"
            ></v-list-item-subtitle>
          </v-list-item-content>
        </template>
      </template>
    </v-autocomplete>
    <br>
    <!-- Related Customer Autocomplete -->
    <v-autocomplete
      v-if="related_customers.length > 0"
      dense
      clearable
      outlined
      color="primary"
      :label="__('Related Customer')"
      v-model="related_customer"
      :items="related_customers"
      item-text="employee_name"
      item-value="name"
      background-color="white"
      :no-data-text="__('No related customer found')"
      hide-details
      :disabled="readonly"
    />
    </v-autocomplete>

    <div class="mb-8">
      <UpdateCustomer></UpdateCustomer>
    </div>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import UpdateCustomer from './UpdateCustomer.vue';
export default {
  props: {
    invoice_doc: {
      type: Object, // Change to Object if you're passing an object
      default: () => ({}), // Default to an empty object
    },
  },

  data: () => ({
    pos_profile: '',
    customers: [],
    customer: '',
    related_customers: [], // Store related customers
    related_customer: '',  // Selected related customer
    readonly: false,
    customer_info: {},
  }),

  components: {
    UpdateCustomer,
  },

  methods: {
    get_customer_names() {
      const vm = this;
      if (this.customers.length > 0) {
        return;
      }
      if (vm.pos_profile.posa_local_storage && localStorage.customer_storage) {
        vm.customers = JSON.parse(localStorage.getItem('customer_storage'));
      }
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_customer_names',
        args: {
          pos_profile: this.pos_profile.pos_profile,
        },
        callback: function (r) {
          if (r.message) {
            vm.customers = r.message;
            console.info('loadCustomers');
            if (vm.pos_profile.posa_local_storage) {
              localStorage.setItem('customer_storage', '');
              localStorage.setItem(
                'customer_storage',
                JSON.stringify(r.message)
              );
            }
          }
        },
      });
    },

    // Fetch related customers based on selected customer
    get_related_customers(customer) {
      const vm = this;
      if (!customer) {
        vm.related_customers = [];
        evntBus.$emit('update_related_customers', vm.related_customers); // Emit empty array when no customer
        return;
      }
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Related Customer',
          filters: {
            parent_customer: customer,
            enabled: 1
          },
          fields: ['name', 'employee_name'],
        },
        callback: function (r) {
          if (r.message) {
            vm.related_customers = r.message;
            evntBus.$emit('update_related_customers', vm.related_customers); // Emit updated related customers
          } else {
            vm.related_customers = [];
            evntBus.$emit('update_related_customers', vm.related_customers); // Emit empty array if no related customers found
          }
        },
      });
    },

    new_customer() {
      evntBus.$emit('open_update_customer', null);
    },
    edit_customer() {
      evntBus.$emit('open_update_customer', this.customer_info);
    },
    customFilter(item, queryText, itemText) {
      const textOne = item.customer_name
        ? item.customer_name.toLowerCase()
        : '';
      const textTwo = item.tax_id ? item.tax_id.toLowerCase() : '';
      const textThree = item.email_id ? item.email_id.toLowerCase() : '';
      const textFour = item.mobile_no ? item.mobile_no.toLowerCase() : '';
      const textFifth = item.name.toLowerCase();
      const searchText = queryText.toLowerCase();

      return (
        textOne.indexOf(searchText) > -1 ||
        textTwo.indexOf(searchText) > -1 ||
        textThree.indexOf(searchText) > -1 ||
        textFour.indexOf(searchText) > -1 ||
        textFifth.indexOf(searchText) > -1
      );
    },
  },

  computed: {},

  created: function () {
    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });
      evntBus.$on('payments_register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });
      evntBus.$on('set_customer', (customer) => {
        this.customer = customer;
      });
      evntBus.$on('add_customer_to_list', (customer) => {
        this.customers.push(customer);
      });
      evntBus.$on('set_customer_readonly', (value) => {
        this.readonly = value;
      });
      evntBus.$on('set_customer_info_to_edit', (data) => {
        this.customer_info = data;
      });
      evntBus.$on('fetch_customer_details', () => {
        this.get_customer_names();
      });
    });
  },

  watch: {
    invoice_doc: {
      immediate: true,
      handler(newVal) {
        // Set related_customer to the value of custom_related_customer from invoice_doc
        if (newVal && newVal.custom_related_customer) {
          this.related_customer = newVal.custom_related_customer;
        } else {
          this.related_customer = ''; // Reset if not available
        }
      },
    },
    customer() {
      evntBus.$emit('update_customer', this.customer);

      this.get_related_customers(this.customer); // Fetch related customers when customer changes
      //this.related_customer = ''; // Clear related customer when customer changes

    },
    related_customer(newVal) {
      evntBus.$emit('set_related_customer', newVal); // Emit after related customer change
    }
  },
};
</script>
