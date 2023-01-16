<template>
  <div>
    <v-btn
    primary
    small
    >
      <div v-if="posa_pos_restaurant_table">
        <span style="font-size: 20px; font-weight: bolder;">
          {{ posa_pos_restaurant_table }}
        </span>
      </div>
      <div v-else>
        {{ __("Select Table") }}
      </div>
      <v-icon mx-3 style="margin: 0px 8px 0px 8px;">mdi-silverware</v-icon>
    </v-btn>
    <v-dialog v-model="tablesDialog" max-width="600px">
      <v-card min-height="500px">
        <v-card-title>
          <span class="headline primary--text">{{ __("Select Table") }}</span>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            dark
            @click="selectTable"
            :disabled="!posa_pos_restaurant_table"
            style="margin-left: 5px; margin-right: 5px"
            >{{ __("UnSelect") }}</v-btn
          >
          <v-btn color="error" dark @click="tablesDialog = false">{{
            __("Close")
          }}</v-btn>
        </v-card-title>
        <v-card-subtitle v-if="posa_pos_restaurant_table">
          <p>
            {{ __("Current Table") }} <span>: {{ posa_pos_restaurant_table }}</span>
          </p>
        </v-card-subtitle>
        <v-card-text class="pa-0">
          <v-container>
            <div>
              <v-row dense class="overflow-y-auto" style="max-height: 800px">
                <v-col
                  v-for="(table, idx) in restaurantTables"
                  :key="idx"
                  xl="3"
                  lg="3"
                  md="3"
                  sm="3"
                  cols="12"
                  min-height="100"
                >
                  <v-card hover="hover" @click="selectTable(table)">
                  <v-card-text
                    class="text-center"
                    style="font-size: larger; font-weight: bolder;"
                  >
                    <v-icon mx-3 style="margin: 0px 8px 0px 8px;">mdi-silverware</v-icon>
                    {{ table.name }}

                </v-card-text>

                  </v-card>
                </v-col>
              </v-row>
            </div>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  props: ['posa_pos_restaurant_table'],
  data: () => ({
    tablesDialog: false,
    pos_profile: {},
    customers: [],
    customer: '',
    readonly: false,
    restaurantTables: []
  }),
  methods: {
    openRestaurantTablesDialog() {
      this.tablesDialog = true;
    },
    selectTable(table) {
      this.tablesDialog = false;
      this.$emit('selectRestaurantTable', table);
    }
  },

  computed: {},

  created: function () {
    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        // this.get_customer_names();
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

      frappe.call(
        {
          method: 'posawesome.api.get_restaurant_tables',
          callback: (r) => {
            this.restaurantTables = r.message;
          }
        }
      )

    });
  },

  watch: {
    // customer() {
    //   evntBus.$emit('update_customer', this.customer);
    // },
  },
};
</script>