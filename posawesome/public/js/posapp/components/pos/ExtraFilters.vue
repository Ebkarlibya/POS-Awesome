<template>
  <div>
    <v-btn
    primary
    small
    >
      <div>
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
            {{ __("extra filters") }} <span>: {{ posa_pos_restaurant_table }}</span>
          </p>
        </v-card-subtitle>
        <v-card-text class="pa-0">
          <v-container>
            extra filters
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
    extraFiltersDialog: false,
    pos_profile: null
  }),
  methods: {
    openRestaurantTablesDialog() {
      this.extraFiltersDialog = true;
    },
  },
  computed: {},
  created: function () {
    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        // this.get_customer_names();
      });
      evntBus.$on('open_extra_filters_dialog', (customer) => {
        this.extraFiltersDialog = true
      });
    });
  },

  watch: {
    // customer() {
    //   evntBus.$emit('update_customer', this.customer);
    // },
  },
};
</script>