<template>
  <div style="max-height: calc(100vh - 40px); height: calc(100vh - 40px)">
    <v-card
      class="selection mx-auto bg-grey-lighten-5 mt-3 d-flex flex-column"
      style="max-height: 100%; height: 100%"
    >
      <v-progress-linear
        :active="loading"
        :indeterminate="loading"
        absolute
        :location="top"
        color="info"
      ></v-progress-linear>
      <div class="flex-grow-0 pa-2 border-b">
        <v-row align="center" class="items px-2 py-1">
          <v-col :cols="pos_profile.posa_input_qty ? 6 : 9" class="pb-0 mb-2">
            <v-text-field
              density="compact"
              clearable
              autofocus
              variant="solo"
              color="primary"
              :label="frappe._('Search Items')"
              hint="Search by item code, serial number, batch no or barcode"
              bg-color="white"
              hide-details
              v-model="debounce_search"
              @keydown.esc="esc_event"
              @keydown.enter="search_onchange"
              @click:clear="clearSearch"
              prepend-inner-icon="mdi-magnify"
              @focus="handleItemSearchFocus"
              ref="debounce_search"
            ></v-text-field>
          </v-col>
          <v-col cols="3" class="pb-0 mb-2" v-if="pos_profile.posa_input_qty">
            <v-text-field
              density="compact"
              variant="solo"
              color="primary"
              :label="frappe._('QTY')"
              bg-color="white"
              hide-details
              v-model.number="qty"
              type="number"
              @keydown.enter="enter_event"
              @keydown.esc="esc_event"
            ></v-text-field>
          </v-col>
          <v-col cols="2" class="pb-0 mb-2">
            <TagFilters />
          </v-col>
          <v-col cols="1" class="pb-0 mb-2">
            <v-btn
              icon
              size="small"
              :disabled="items_view !== 'list'"
              @click="showColumnSettings = true"
              title="Column Settings"
            >
              <v-icon>mdi-cog</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </div>
      <div class="flex-grow-1 overflow-hidden border-b">
        <v-col cols="12" class="pt-0 mt-0 h-100">
          <div class="h-100">
            <div v-if="items_view == 'card'" class="h-100">
              <v-row class="overflow-y-auto" style="height: 100%; max-height: 100%">
                <v-col
                  v-for="(item, idx) in filtered_items"
                  :key="idx"
                  xl="2"
                  lg="3"
                  md="6"
                  sm="6"
                  cols="6"
                  min-height="50"
                >
                  <v-card hover="hover" @click="add_item(item)">
                    <v-img
                      :src="item.image || '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'"
                      class="text-white align-end"
                      gradient="to bottom, rgba(0,0,0,0), rgba(0,0,0,0.4)"
                      height="100px"
                    >
                      <v-card-text
                        v-text="item.item_name"
                        class="text-caption px-1 pb-0"
                      ></v-card-text>
                    </v-img>
                    <v-card-text class="text--primary pa-1">
                      <div class="d-flex align-center justify-space-between">
                        <div class="d-flex flex-column align-center">
                          <span class="text-caption text-primary" style="white-space: normal; word-break: break-word;">
                            {{ currencySymbol(pos_profile.currency) || "" }}
                            {{ format_currency(item.rate, pos_profile.currency, 4) }}
                          </span>
                          <span v-if="pos_profile.posa_allow_multi_currency && selected_currency !== pos_profile.currency" class="text-caption text-success" style="white-space: normal; word-break: break-word;">
                            {{ currencySymbol(selected_currency) || "" }}
                            {{ format_currency(getConvertedRate(item), selected_currency, 4) }}
                          </span>
                        </div>
                        <v-btn
                          v-if="invoiceType==='Order'"
                          size="small"
                          icon="mdi-information"
                          @click.stop="showItemDetails(item)"
                          :title="__('Click to show item details')"
                        ></v-btn>
                        <v-btn
                          v-else
                          size="small"
                          icon="mdi-database-eye"
                          @click.stop="showWarehousesQuantities(item)"
                          :title="__('Click to show quantity per warehouses')"
                        ></v-btn>
                      </div>
                      <div class="text-caption golden--text">
                        {{ format_number(item.actual_qty, 4) || 0 }}
                        {{ item.stock_uom || "" }}
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>

            <div v-if="items_view == 'list'" class="h-100">
              <div class="overflow-y-auto" style="height: 100%; max-height: 100%">
                <v-data-table
                  :headers="getVisibleHeaders()"
                  :items="filtered_items"
                  item-key="item_code"
                  item-value="item-"
                  class="elevation-0 sleek-data-table"
                  :items-per-page="itemsPerPage"
                  hide-default-footer
                  @click:row="click_item_row"
                  dense
                  :style="autoAdjustWidths ? '' : 'table-layout: fixed;'"
                >
                  <template v-slot:item.rate="{ item }">
                    <div>
                      <div class="text-primary">
                        {{ currencySymbol(pos_profile.currency) }}
                        {{ format_currency(item.rate, pos_profile.currency, 4) }}
                      </div>
                      <div v-if="pos_profile.posa_allow_multi_currency && selected_currency !== pos_profile.currency" class="text-success">
                        {{ currencySymbol(selected_currency) }}
                        {{ format_currency(getConvertedRate(item), selected_currency, 4) }}
                      </div>
                    </div>
                  </template>
                  <template v-slot:item.item_group="{ item }">
                    <span>{{ item.item_group || '' }}</span>
                  </template>

                  <template v-slot:item.brand="{ item }">
                    <span>{{ item.brand || '' }}</span>
                  </template>

                  <template v-slot:item.description="{ item }">
                    <div class="text-caption" v-html="item.description || ''"></div>
                  </template>

                  <template v-slot:item.actual_qty="{ item }">
                    <span class="golden--text">
                      {{ format_number(item.actual_qty, 4) }}
                    </span>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn
                      v-if="invoiceType==='Order'"
                      icon
                      size="large"
                      density="compact"
                      @click.stop="showItemDetails(item)"
                      :title="__('Click to show item details')"
                    >
                      <v-icon size="28">mdi-information</v-icon>
                    </v-btn>
                    <v-btn
                      v-else
                      icon
                      size="large"
                      density="compact"
                      @click.stop="showWarehousesQuantities(item)"
                      :title="__('Click to show quantity per warehouses')"
                    >
                      <v-icon size="28">mdi-database-eye</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </div>
            </div>
          </div>
        </v-col>
      </div>

      <div class="flex-grow-0">
        <v-card class="cards mb-0 pa-2 bg-grey-lighten-5">
          <!-- Item Group Filter -->
          <v-row
            no-gutters
            align="center"
            justify="center"
            class="pb-3 border-b"
          >
            <v-col cols="12">
              <div style="max-height: 120px; overflow-y: auto">
                <item-group-multi-select
                  :itemGroups="items_group"
                  :label="frappe._('Items Group')"
                  @click="setFastItemGroupFilter"
                />
              </div>
            </v-col>
          </v-row>
          <!-- Item Group Filter End -->

          <v-row no-gutters align="center" justify="center">
            <!-- <v-col cols="12">
              <v-select
                :items="items_group"
                :label="frappe._('Items Group')"
                density="compact"
                variant="solo"
                hide-details
                v-model="item_group"
              ></v-select>
            </v-col> -->
            <v-col :cols="pos_profile.posa_new_line ? 3 : 6" class="mt-1">
              <v-btn-toggle
                v-model="items_view"
                color="primary"
                group
                density="compact"
                rounded
              >
                <v-btn size="small" value="list">{{ __("List") }}</v-btn>
                <v-btn size="small" value="card">{{ __("Card") }}</v-btn>
              </v-btn-toggle>
            </v-col>
            <v-col cols="3" class="mt-1" v-if="pos_profile.posa_new_line">
              <v-btn-toggle
                v-model="new_line"
                color="primary"
                group
                density="compact"
                rounded
              >
                <v-btn size="small" :value="true">{{ __("New Line") }}</v-btn>
                <v-btn size="small" :value="false">{{ __("One Line") }}</v-btn>
              </v-btn-toggle>
            </v-col>
            <v-col cols="2" class="mt-1">
              <v-btn
                size="small"
                block
                color="primary"
                variant="text"
                @click="show_coupons"
              >
                {{ couponsCount }} {{ __("Coupons") }}
              </v-btn>
            </v-col>
            <v-col cols="4" class="mt-1">
              <v-btn
                size="small"
                block
                color="primary"
                variant="text"
                @click="show_offers"
              >
                {{ offersCount }} {{ __("Offers") }}: {{ appliedOffersCount }} {{ __("Applied") }}
              </v-btn>
            </v-col>
          </v-row>
        </v-card>
      </div>
    </v-card>
  </div>
  <ColumnSettings
    v-model:show="showColumnSettings"
    :availableHeaders="availableHeadersConfig"
    @columns-changed="handleColumnsChanged"
  />
</template>

<script>

import format from "../../format";
import _ from "lodash";
import ItemGroupMultiSelect from "./ItemGroupMultiSelect.vue";
import TagFilters from "./TagFilters.vue";
import ColumnSettings from "./ColumnSettings.vue";

export default {
  components: {
    ItemGroupMultiSelect,
    TagFilters,
    ColumnSettings,
  },

  mixins: [format],
  data: () => ({
    pos_profile: "",
    pos_settings_panel: "",
    flags: {},
    items_view: "list",
    item_group: "ALL",
    loading: false,
    items_group: ["ALL"],
    items: [],
    search: "",
    first_search: "",
    search_backup: "",
    itemsPerPage: 1000,
    offersCount: 0,
    appliedOffersCount: 0,
    couponsCount: 0,
    appliedCouponsCount: 0,
    customer_price_list: null,
    customer: null,
    new_line: false,
    qty: 1,
    refresh_interval: null,
    currentRequest: null,
    abortController: null,
    items_loaded: false,
    selected_currency: "",
    exchange_rate: 1,
    pos_tags_filters: [],
    invoiceType: "Invoice",
    columnSettings: {},
    showColumnSettings: false,
    availableHeadersConfig: [
      {
        title: __("Name"),
        key: "item_name",
        hideable: false, // Cannot be hidden
        widthConfigurable: true,
        defaultWidth: "40%"
      },
      {
        title: __("Code"),
        key: "item_code",
        hideable: true,
        widthConfigurable: true,
        defaultWidth: "15%",
        defaultVisible: true
      },
      {
        title: __("Rate"),
        key: "rate",
        hideable: true,
        widthConfigurable: true,
        defaultWidth: "15%",
        defaultVisible: true
      },
      {
        title: __("Ava. QTY"),
        key: "actual_qty",
        hideable: true,
        widthConfigurable: true,
        defaultWidth: "15%",
        defaultVisible: true
      },
      {
        title: __("UOM"),
        key: "stock_uom",
        hideable: true,
        widthConfigurable: true,
        defaultWidth: "10%",
        defaultVisible: true
      },
      // Additional columns (hidden by default)
      {
        title: __("Item Group"),
        key: "item_group",
        hideable: true,
        widthConfigurable: true,
        defaultWidth: "15%",
        defaultVisible: false
      },
      {
        title: __("Brand"),
        key: "brand",
        hideable: true,
        widthConfigurable: true,
        defaultWidth: "15%",
        defaultVisible: false
      },
      {
        title: __("Description"),
        key: "description",
        hideable: true,
        widthConfigurable: true,
        defaultWidth: "20%",
        defaultVisible: false
      },
      {
        title: __("Actions"),
        key: "actions",
        hideable: false, // Cannot be hidden
        widthConfigurable: false,
        defaultWidth: "5%"
      }
    ],
    columnWidths: {},
    autoAdjustWidths: true,
  }),

  watch: {
    filtered_items(new_value, old_value) {
      if (!this.pos_profile.pose_use_limit_search) {
        if (new_value.length != old_value.length) {
          this.update_items_details(new_value);
        }
      }
    },
    customer() {
      if (this.items_loaded && this.filtered_items && this.filtered_items.length > 0) {
        this.update_items_details(this.filtered_items);
      } else {
        this.get_items();
      }
    },
    new_line() {
      this.eventBus.emit("set_new_line", this.new_line);
    },
  },

  methods: {
    showWarehousesQuantities(item) {
      this.eventBus.emit('show_warehouse_dialog', item);
    },
    showItemDetails(item) {
      this.eventBus.emit('show_item_details_dialog', item);
    },
    show_offers() {
      this.eventBus.emit("show_offers", "true");
    },
    show_coupons() {
      this.eventBus.emit("show_coupons", "true");
    },
    get_items() {
      if (!this.pos_profile) {
        console.error("No POS Profile");
        return;
      }
      
      // If items are already loaded and it's not a specific search or customer change, don't reload
      if (this.items_loaded && !this.first_search && !this.pos_profile.pose_use_limit_search) {
        console.info("Items already loaded, skipping reload");
        // Still update quantities for displayed items
        if (this.filtered_items && this.filtered_items.length > 0) {
          this.update_items_details(this.filtered_items);
        }
        return;
      }
      
      const vm = this;
      this.loading = true;
      let search = this.get_search(this.first_search);
      let gr = "";
      let sr = "";
      if (search) {
        sr = search;
      }
      if (vm.item_group != "ALL") {
        gr = vm.item_group.toLowerCase();
      }
      if (
        vm.pos_profile.posa_local_storage &&
        localStorage.items_storage &&
        !vm.pos_profile.pose_use_limit_search
      ) {
        vm.items = JSON.parse(localStorage.getItem("items_storage"));
        this.eventBus.emit("set_all_items", vm.items);
        vm.loading = false;
        vm.items_loaded = true;
        
        // Even when loading from localStorage, refresh the quantities
        setTimeout(() => {
          if (vm.filtered_items && vm.filtered_items.length > 0) {
            vm.update_items_details(vm.filtered_items);
          }
        }, 300);
      }
      frappe.call({
        method: "posawesome.posawesome.api.posapp.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: gr,
          search_value: sr,
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message) {
            vm.items = r.message;

            vm.eventBus.emit("set_all_items", vm.items);
            vm.loading = false;
            vm.items_loaded = true;
            vm.update_items_details(vm.items);
            console.info("Items Loaded");
            vm.$nextTick(() => {
              if(vm.search) vm.search_onchange();
            });
            
            // Always refresh quantities after items are loaded
            setTimeout(() => {
              if (vm.filtered_items && vm.filtered_items.length > 0) {
                vm.update_items_details(vm.filtered_items);
              }
            }, 300);
            
            if (
              vm.pos_profile.posa_local_storage &&
              !vm.pos_profile.pose_use_limit_search
            ) {
              localStorage.setItem("items_storage", "");
              try {
                localStorage.setItem(
                  "items_storage",
                  JSON.stringify(r.message)
                );
              } catch (e) {
                console.error(e);
              }
            }
            if (vm.pos_profile.pose_use_limit_search) {
              vm.enter_event();
            }
          }
        },
      });
    },
    get_items_groups() {
      if (!this.pos_profile) {
        console.log("No POS Profile");
        return;
      }
      if (this.pos_profile.item_groups.length > 0) {
        this.pos_profile.item_groups.forEach((element) => {
          if (element.item_group !== "All Item Groups") {
            this.items_group.push(element.item_group);
          }
        });
      } else {
        const vm = this;
        frappe.call({
          method: "posawesome.posawesome.api.posapp.get_items_groups",
          args: {},
          callback: function (r) {
            if (r.message) {
              r.message.forEach((element) => {
                vm.items_group.push(element.name);
              });
            }
          },
        });
      }
    },
    getItemsHeaders() {
      const items_headers = [
        {
          title: __("Name"),
          align: "start",
          sortable: true,
          key: "item_name",
          width: "40%",
        },
        {
          title: __("Code"),
          align: "start",
          sortable: true,
          key: "item_code",
        },
        { title: __("Rate"), key: "rate", align: "start" },
        { title: __("Ava. QTY"), key: "actual_qty", align: "start" },
        { title: __("UOM"), key: "stock_uom", align: "start" },
      ];
      if (!this.pos_profile.posa_display_item_code) {
        items_headers.splice(1, 1);
      }
      items_headers.push({
        title: __("Actions"),
        key: "actions",
        align: "end",
        sortable: false,
      });

      return items_headers;
    },
    click_item_row(event, { item }) {
      this.add_item(item)
    },
    add_item(item) {
      item = {
        ...item,
        item_selected_warehouse: this.pos_profile.warehouse,
        item_selected_warehouse_actual_qty: item.actual_qty
      };
      if (item.has_variants) {
        this.eventBus.emit(
          "open_variants_model",
          {
            'item': item,
            'items': this.items
          }
        );
      } else {
        // // Test it in version 15 (Not ETEMS Custom)
        // if (item.actual_qty === 0 && this.pos_profile.posa_display_items_in_stock) {
        //   this.eventBus.emit("show_message", {
        //     title: `No stock available for ${item.item_name}`,
        //     color: "warning",
        //   });
        //   this.update_items_details([item]);
        //   return;
        // }
        
        // Ensure UOMs are initialized before adding the item
        if (!item.item_uoms || item.item_uoms.length === 0) {
          // If UOMs are not available, fetch them first
          this.update_items_details([item]);
          
          // Add stock UOM as fallback
          if (!item.item_uoms || item.item_uoms.length === 0) {
            item.item_uoms = [{ uom: item.stock_uom, conversion_factor: 1.0 }];
          }
        }
        
        // Convert rate if multi-currency is enabled
        if (this.pos_profile.posa_allow_multi_currency && 
            this.selected_currency !== this.pos_profile.currency) {
          // Store original rate as base_rate
          item.base_rate = item.rate;
          item.base_price_list_rate = item.price_list_rate;
          
          // Set converted rates
          item.rate = this.getConvertedRate(item);
          item.price_list_rate = this.getConvertedRate(item);
          
          // Set currency
          item.currency = this.selected_currency;
        }

        if (!item.qty || item.qty === 1) {
          item.qty = Math.abs(this.qty);
        }
        this.eventBus.emit("add_item", item);
        this.qty = 1;
      }
    },
    enter_event() {
      let match = false;
      if (!this.filtered_items.length || !this.first_search) {
        return;
      }
      const qty = this.get_item_qty(this.first_search);
      const new_item = { ...this.filtered_items[0] };
      new_item.qty = flt(qty);
      new_item.item_barcode.forEach((element) => {
        if (this.search == element.barcode) {
          new_item.uom = element.posa_uom;
          match = true;
        }
      });
      if (
        !new_item.to_set_serial_no &&
        new_item.has_serial_no &&
        this.pos_profile.posa_search_serial_no
      ) {
        new_item.serial_no_data.forEach((element) => {
          if (this.search && element.serial_no == this.search) {
            new_item.to_set_serial_no = this.first_search;
            match = true;
          }
        });
      }
      if (this.flags.serial_no) {
        new_item.to_set_serial_no = this.flags.serial_no;
      }
      if (
        !new_item.to_set_batch_no &&
        new_item.has_batch_no &&
        this.pos_profile.posa_search_batch_no
      ) {
        new_item.batch_no_data.forEach((element) => {
          if (this.search && element.batch_no == this.search) {
            new_item.to_set_batch_no = this.first_search;
            new_item.batch_no = this.first_search;
            match = true;
          }
        });
      }
      if (this.flags.batch_no) {
        new_item.to_set_batch_no = this.flags.batch_no;
      }
      if (match) {
        this.add_item(new_item);
        this.search = null;
        this.first_search = null;
        this.debounce_search = null;
        this.flags.serial_no = null;
        this.flags.batch_no = null;
        this.qty = 1;
        this.$refs.debounce_search.focus();
      }
    },
    search_onchange: _.debounce(function(newSearchTerm) {
      const vm = this;
      
      let term = "";
      if (typeof newSearchTerm === "string") {
        term = newSearchTerm;
      } else if (newSearchTerm && typeof newSearchTerm === "object") {
        // Could be an Event or other object
        if (newSearchTerm.target && typeof newSearchTerm.target.value === "string") {
          term = newSearchTerm.target.value;
        } else {
          term = vm.first_search || vm.debounce_search || vm.search || "";
        }
      } else {
        term = vm.first_search || vm.debounce_search || vm.search || "";
      }

      // Normalize and assign safely (only when it's a string)
      if (term && typeof term === "string") {
        term = term.trim().replace(/\s+/g, " ");
        vm.search = term;
      } else {
        // ensure vm.search becomes empty string, not some non-string value
        vm.search = "";
      }
      
      if (vm.pos_profile.pose_use_limit_search) {
        vm.get_items();
      } else {
        // Save the current filtered items before search to maintain quantity data
        const current_items = [...vm.filtered_items];

        if (vm.search && vm.search.length >= 3) {
          vm.enter_event();
        }

        // After search, update quantities for newly filtered items
        if (vm.filtered_items && vm.filtered_items.length > 0) {
          setTimeout(() => {
            vm.update_items_details(vm.filtered_items);
          }, 300);
        }
      }
    }, 300),
    get_item_qty(first_search) {
      let scal_qty = Math.abs(this.qty);
      if (first_search.startsWith(this.pos_profile.posa_scale_barcode_start)) {
        let pesokg1 = first_search.substr(7, 5);
        let pesokg;
        if (pesokg1.startsWith("0000")) {
          pesokg = "0.00" + pesokg1.substr(4);
        } else if (pesokg1.startsWith("000")) {
          pesokg = "0.0" + pesokg1.substr(3);
        } else if (pesokg1.startsWith("00")) {
          pesokg = "0." + pesokg1.substr(2);
        } else if (pesokg1.startsWith("0")) {
          pesokg =
            pesokg1.substr(1, 1) + "." + pesokg1.substr(2, pesokg1.length);
        } else if (!pesokg1.startsWith("0")) {
          pesokg =
            pesokg1.substr(0, 2) + "." + pesokg1.substr(2, pesokg1.length);
        }
        scal_qty = pesokg;
      }
      return scal_qty;
    },
    get_search(first_search) {
      let search_term = "";

      // Normalize the search input - trim and collapse multiple spaces
      if (first_search) {
        first_search = first_search.trim().replace(/\s+/g, ' ');
      }

      if (
        first_search &&
        first_search.startsWith(this.pos_profile.posa_scale_barcode_start)
      ) {
        search_term = first_search.substr(0, 7);
      } else {
        search_term = first_search;
      }
      return search_term;
    },
    esc_event() {
      this.search = null;
      this.first_search = null;
      this.search_backup = null;
      this.qty = 1;
      this.$refs.debounce_search.focus();
    },
    update_items_details(items) {
      // set debugger
      const vm = this;
      if (!items || !items.length) return;

      // Cancel previous request
      if (vm.currentRequest) {
        vm.abortController.abort();
        vm.currentRequest = null;
      }

      vm.abortController = new AbortController();
      
      vm.currentRequest = frappe.call({
        method: "posawesome.posawesome.api.posapp.get_items_details",
        args: {
          pos_profile: vm.pos_profile,
          items_data: items,
        },
        freeze: true,
        signal: vm.abortController.signal,
        callback: function(r) {
          if (r.message) {
            let qtyChanged = false;
            
            items.forEach((item) => {
              const updated_item = r.message.find(
                (element) => element.item_code == item.item_code
              );
              if (updated_item) {
                // Save previous quantity for comparison
                const prev_qty = item.actual_qty;
                
                item.actual_qty = updated_item.actual_qty;
                item.serial_no_data = updated_item.serial_no_data;
                item.warehouses_serial_no_data = updated_item.warehouses_serial_no_data;
                item.batch_no_data = updated_item.batch_no_data;
                
                // Properly handle UOMs data
                if (updated_item.item_uoms && updated_item.item_uoms.length > 0) {
                  item.item_uoms = updated_item.item_uoms;
                } else if (!item.item_uoms || !item.item_uoms.length) {
                  // If no UOMs found, at least add the stock UOM
                  item.item_uoms = [{ uom: item.stock_uom, conversion_factor: 1.0 }];
                }
                
                item.has_batch_no = updated_item.has_batch_no;
                item.has_serial_no = updated_item.has_serial_no;
                
                // Log and track significant quantity changes
                if (prev_qty > 0 && item.actual_qty === 0) {
                  console.log(`Item ${item.item_code} quantity changed from ${prev_qty} to 0`);
                  qtyChanged = true;
                }
              }
            });
            
            // Force update if any item's quantity changed significantly
            if (qtyChanged) {
              vm.$forceUpdate();
            }
          }
        },
        error: function(err) {
          if (err.name !== 'AbortError') {
            console.error("Error fetching item details:", err);
            setTimeout(() => {
              vm.update_items_details(items);
            }, 1000);
          }
        }
      });
      
      // Cleanup on component destroy
      this.cleanupBeforeDestroy = () => {
        if (vm.abortController) {
          vm.abortController.abort();
        }
      };
    },
    update_cur_items_details() {
      if (this.filtered_items && this.filtered_items.length > 0) {
        this.update_items_details(this.filtered_items);
      }
    },
    scan_barcoud() {
      const vm = this;
      try {
        // Check if scanner is already attached to document
        if (document._scannerAttached) {
          return;
        }
        
        onScan.attachTo(document, {
          suffixKeyCodes: [],
          keyCodeMapper: function (oEvent) {
            oEvent.stopImmediatePropagation();
            return onScan.decodeKeyEvent(oEvent);
          },
          onScan: function (sCode) {
            setTimeout(() => {
              vm.trigger_onscan(sCode);
            }, 300);
          },
        });
        
        // Mark document as having scanner attached
        document._scannerAttached = true;
      } catch (error) {
        console.warn('Scanner initialization error:', error.message);
      }
    },
    trigger_onscan(sCode) {
      if (this.filtered_items.length == 0) {
        this.eventBus.emit("show_message", {
          title: `No Item has this barcode "${sCode}"`,
          color: "error",
        });
        frappe.utils.play_sound("error");
      } else {
        if(this.pos_settings_panel && this.pos_settings_panel.enable_barcode_auto_add) {
          this.enter_event();
        }
      }
    },
    setFastItemGroupFilter(event, groupName) {
      if (this.item_group === groupName) {
        this.item_group = "ALL";
      } else {
        this.item_group = groupName;
      }
    },
    generateWordCombinations(inputString) {
      const words = inputString.split(" ");
      const wordCount = words.length;
      const combinations = [];

      // Helper function to generate all permutations
      function permute(arr, m = []) {
        if (arr.length === 0) {
          combinations.push(m.join(" "));
        } else {
          for (let i = 0; i < arr.length; i++) {
            const current = arr.slice();
            const next = current.splice(i, 1);
            permute(current.slice(), m.concat(next));
          }
        }
      }

      permute(words);

      return combinations;
    },
    clearSearch() {
      this.search_backup = this.first_search;
      this.first_search = "";
      this.search = "";
      // No need to call get_items() again
    },
    
    restoreSearch() {
      if (this.first_search === "") {
        this.first_search = this.search_backup;
        this.search = this.search_backup;
        // No need to reload items when focus is lost
      }
    },
    handleItemSearchFocus() {
      this.first_search = "";
      this.search = "";
      // Optionally, you might want to also clear search_backup if the behaviour should be a full reset on focus
      // this.search_backup = ""; 
    },
    getConvertedRate(item) {
      if (!item.rate) return 0;
      if (!this.exchange_rate) return item.rate;
      
      // If exchange rate is 300 PKR = 1 USD
      // To convert PKR to USD: divide by exchange rate
      // Example: 3000 PKR / 300 = 10 USD
      const convertedRate = item.rate / this.exchange_rate;
      return this.flt(convertedRate, 4);
    },
    currencySymbol(currency) {
      return get_currency_symbol(currency);
    },
    format_currency(value, currency, precision) {
      if (!value) return '0';
      
      // Convert to string for checking decimal points
      let valueStr = value.toString();
      
      // If value has decimal points, show 4 decimal places
      if (valueStr.includes('.')) {
        return flt(value, 4).toString();
      }
      
      // For whole numbers, return as is
      return valueStr;
    },
    format_number(value, precision) {
      if (!value) return '0';
      
      // Convert to string for checking decimal points
      let valueStr = value.toString();
      
      // If value has decimal points, show 4 decimal places
      if (valueStr.includes('.')) {
        return flt(value, 4).toString();
      }
      
      // For whole numbers, return as is
      return valueStr;
    },
    hasDecimalPrecision(value) {
      // Check if the value has any decimal precision when multiplied by exchange rate
      if (this.exchange_rate && this.exchange_rate !== 1) {
        let convertedValue = value * this.exchange_rate;
        return !Number.isInteger(convertedValue);
      }
      return !Number.isInteger(value);
    },
    getVisibleHeaders() {
      const items_headers = [
        {
          title: __("Name"),
          align: "start",
          sortable: true,
          key: "item_name",
          width: this.columnWidths.item_name || "40%"
        },
        {
          title: __("Code"),
          align: "start",
          sortable: true,
          key: "item_code",
          width: this.columnWidths.item_code || "15%"
        },
        { 
          title: __("Rate"), 
          key: "rate", 
          align: "start",
          width: this.columnWidths.rate || "15%"
        },
        { 
          title: __("Ava. QTY"), 
          key: "actual_qty", 
          align: "start",
          width: this.columnWidths.actual_qty || "15%"
        },
        { 
          title: __("UOM"), 
          key: "stock_uom", 
          align: "start",
          width: this.columnWidths.stock_uom || "10%"
        },
        // Additional columns
        { 
          title: __("Item Group"), 
          key: "item_group", 
          align: "start",
          width: this.columnWidths.item_group || "15%"
        },
        { 
          title: __("Brand"), 
          key: "brand", 
          align: "start",
          width: this.columnWidths.brand || "15%"
        },
        { 
          title: __("Description"), 
          key: "description", 
          align: "start",
          width: this.columnWidths.description || "20%"
        },
        {
          title: __("Actions"),
          key: "actions",
          align: "end",
          sortable: false,
          width: this.columnWidths.actions || "5%"
        }
      ];
      
      // Filter headers based on column settings and display settings
      return items_headers.filter(header => {
        // Always show actions column and name column
        if (header.key === 'actions' || header.key === 'item_name') return true;
        
        // Hide item_code if disabled in POS profile
        if (!this.pos_profile.posa_display_item_code && header.key === 'item_code') return false;
        
        // Check column visibility settings
        return this.columnSettings[header.key] !== false;
      });
    },
    handleColumnsChanged(settings) {
      this.columnSettings = settings.visibility;
      this.columnWidths = settings.widths;
      this.autoAdjustWidths = settings.autoAdjust;
      
      // Apply auto-adjust if enabled
      if (this.autoAdjustWidths) {
        this.applyAutoColumnWidths();
      }
      
      this.$forceUpdate();
    },
    applyAutoColumnWidths() {
      // Reset to default widths for auto-adjust
      this.columnWidths = {};
      
      // You could add more sophisticated logic here to calculate
      // optimal column widths based on content
      this.availableHeadersConfig.forEach(header => {
        if (header.defaultWidth) {
          this.columnWidths[header.key] = header.defaultWidth;
        }
      });
    },
  },

  computed: {
    filtered_items() {
      // console.log(this.pos_profile);
      this.search = this.get_search(this.first_search);

      // Test it in version 15 (Not ETEMS Custom)
      if (this.pos_profile.pose_use_limit_search) {
        const items_list = this.items.slice(0, this.pos_profile.custom_posa_items_per_page);
        items_list.forEach(item => {
          if (item.actual_qty === undefined) {
            item.actual_qty = 0;
          }
        });
        return items_list;
      }

      // if (!this.pos_profile.pose_use_limit_search) {
      let filtered_list = [];
      let filtered_group_list = [];
      if (this.item_group != "ALL") {
        filtered_group_list = this.items.filter((item) => {
          const itemGroup = item.item_group || '';
          return itemGroup.toLowerCase().includes(this.item_group.toLowerCase());
        });
      } else {
        filtered_group_list = this.items;
      }
      if (this.pos_tags_filters && this.pos_tags_filters.length > 0) {
        filtered_group_list = filtered_group_list.filter((fItem) => {
          return fItem.pos_tags.some((itemPosTag) => {
            return this.pos_tags_filters.some(
              (filterPosTag) => filterPosTag.tag_name === itemPosTag.tag_name
            );
          });
        });
      }
      // ETMS
      if (!this.search || this.search.length < 3) {
        let filtered = [];
        if (
          this.pos_profile.posa_show_template_items &&
          this.pos_profile.posa_hide_variants_items
        ) {
          filtered = filtered_group_list
            .filter((item) => !item.variant_of)
            .slice(0, this.pos_profile.custom_posa_items_per_page);
        } else {
          filtered = filtered_group_list.slice(
            0,
            this.pos_profile.custom_posa_items_per_page
          );
        }
        
        // Ensure quantities are defined
        filtered.forEach(item => {
          if (item.actual_qty === undefined) {
            item.actual_qty = 0;
          }
        });
        
        return filtered;
      } else if (this.search) {
        filtered_list = filtered_group_list.filter((item) => {
          let found = false;
          for (let element of item.item_barcode) {
            if (element.barcode == this.search) {
              found = true;
              break;
            }
          }
          return found;
        });
        if (filtered_list.length == 0) {
          filtered_list = filtered_group_list.filter((item) =>
            item.item_code.toLowerCase().includes(this.search.toLowerCase())
          );
          if (filtered_list.length == 0) {
            // filtered_list = filtered_group_list.filter((item) =>
            //   item.item_name.toLowerCase().includes(this.search.toLowerCase())
            // );

            // Test it in version 15 (Not ETEMS Custom)
            const search_combinations = this.generateWordCombinations(
              this.search
            );
            filtered_list = filtered_group_list.filter((item) => {
              let found = false;
              for (let element of search_combinations) {
                element = element.toLowerCase().trim();
                let element_regex = new RegExp(
                  `.*${element.split("").join(".*")}.*`
                );
                if (element_regex.test(item.item_name.toLowerCase())) {
                  found = true;
                  break;
                }
              }
              return found;
            });
          }
          if (
            filtered_list.length == 0 &&
            this.pos_profile.posa_search_serial_no
          ) {
            filtered_list = filtered_group_list.filter((item) => {
              let found = false;
              for (let element of item.serial_no_data) {
                if (element.serial_no == this.search) {
                  found = true;
                  this.flags.serial_no = null;
                  this.flags.serial_no = this.search;
                  break;
                }
              }
              return found;
            });
          }
          if (
            filtered_list.length == 0 &&
            this.pos_profile.posa_search_batch_no
          ) {
            filtered_list = filtered_group_list.filter((item) => {
              let found = false;
              for (let element of item.batch_no_data) {
                if (element.batch_no == this.search) {
                  found = true;
                  this.flags.batch_no = null;
                  this.flags.batch_no = this.search;
                  break;
                }
              }
              return found;
            });
          }
        }
      }
      
      let final_filtered_list = [];
      if (
        this.pos_profile.posa_show_template_items &&
        this.pos_profile.posa_hide_variants_items
      ) {
        final_filtered_list = filtered_list
          .filter((item) => !item.variant_of)
          .slice(0, this.pos_profile.custom_posa_items_per_page);
      } else {
        final_filtered_list = filtered_list.slice(
          0,
          this.pos_profile.custom_posa_items_per_page
        );
      }

      // Test it in version 15 (ETEMS Custom)
      // Implement fuzzy search using Levenshtein distance algorithm without slicing
      // if (final_filtered_list.length == 0 && this.search) {
      //   final_filtered_list = filtered_group_list.filter((items) => {
      //     return levenshteinDistance(
      //       items.item_name.toLowerCase(),
      //       this.search.toLowerCase()
      //     );
      //   });
      // }
      // Implement fuzzy search using Levenshtein distance algorithm with slicing
      if (final_filtered_list.length == 0 && this.search) {
        const fallback = filtered_group_list.filter((items) => {
          return levenshteinDistance(
            items.item_name.toLowerCase(),
            this.search.toLowerCase()
          );
        });
        final_filtered_list = fallback.slice(
          0,
          this.pos_profile.custom_posa_items_per_page
        );
      }
      
      // Test it in version 15 (Not ETEMS Custom)
      // Ensure quantities are defined for each item
      final_filtered_list.forEach(item => {
        if (item.actual_qty === undefined) {
          item.actual_qty = 0;
        }
      });
      
      // Test it in version 15 (Not ETEMS Custom)
      // Force request quantity update for filtered items
      if (final_filtered_list.length > 0) {
        setTimeout(() => {
          this.update_items_details(final_filtered_list);
        }, 100);
      }
      
      return final_filtered_list;

      function levenshteinDistance(itemName, searchQuery) {
        let searchWords = searchQuery.split(" ");
        for (let i = 0; i < searchWords.length; i++) {
          if (!itemName.includes(searchWords[i])) {
            return false;
          }
        }
        return true;
      }
      // }
      // else {
      //   filtered_list = [];

      //   if (filtered_list.length == 0 && this.search) {
      //     filtered_list = filtered_group_list.filter((items) => {
      //       return levenshteinDistance(
      //         items.item_name.toLowerCase(),
      //         this.search.toLowerCase()
      //       );
      //     });
      //     return filtered_list;
      //   } else {
      //     const items_list = this.items.slice(0, 50);
        
      //     // Ensure quantities are defined
      //     items_list.forEach(item => {
      //       if (item.actual_qty === undefined) {
      //         item.actual_qty = 0;
      //       }
      //     });
          
      //     return items_list;
      //   }
      // }
      // function levenshteinDistance(itemName, searchQuery) {
      //   let searchWords = searchQuery.split(" ");
      //   for (let i = 0; i < searchWords.length; i++) {
      //     if (!itemName.includes(searchWords[i])) {
      //       return false;
      //     }
      //   }
      //   return true;
      // }
    },
    debounce_search: {
      get() {
        return this.first_search;
      },
      set: _.debounce(function (newValue) {
        if (newValue) {
            this.first_search = newValue.trim().replace(/\s+/g, ' ');
        } else {
            this.first_search = newValue;
        }
      }, 300),
    },
  },

  created: function () {
    this.$nextTick(function () { });

    // Load column settings
    const savedColumnSettings = localStorage.getItem('posawesome_column_settings');
    if (savedColumnSettings) {
      this.columnSettings = JSON.parse(savedColumnSettings);
    } else {
      // Set default column settings for all available headers
      this.columnSettings = {};
      this.availableHeadersConfig.forEach(header => {
        this.columnSettings[header.key] = header.defaultVisible !== false;
      });
    }
    
    // Load column width settings
    const savedWidths = localStorage.getItem('posawesome_column_widths');
    if (savedWidths) {
      this.columnWidths = JSON.parse(savedWidths);
    } else {
      // Set default widths for all available headers
      this.columnWidths = {};
      this.availableHeadersConfig.forEach(header => {
        if (header.defaultWidth) {
          this.columnWidths[header.key] = header.defaultWidth;
        }
      });
    }
    
    // Load auto-adjust setting
    const savedAutoAdjust = localStorage.getItem('posawesome_auto_adjust_widths');
    this.autoAdjustWidths = savedAutoAdjust ? JSON.parse(savedAutoAdjust) : true;
    
    // Apply auto-adjust if enabled
    if (this.autoAdjustWidths) {
      this.applyAutoColumnWidths();
    }

    this.eventBus.on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;
      this.pos_settings_panel = data.pos_settings_panel;
      this.selected_currency = this.pos_profile.currency;
      this.get_items();
      this.get_items_groups();
      this.items_view = this.pos_profile.posa_default_card_view
        ? "card"
        : "list";
    });
    this.eventBus.on("update_cur_items_details", () => {
      this.update_cur_items_details();
    });
    this.eventBus.on("update_offers_counters", (data) => {
      this.offersCount = data.offersCount;
      this.appliedOffersCount = data.appliedOffersCount;
    });
    this.eventBus.on("update_coupons_counters", (data) => {
      this.couponsCount = data.couponsCount;
      this.appliedCouponsCount = data.appliedCouponsCount;
    });
    this.eventBus.on("update_customer_price_list", (data) => {
      this.customer_price_list = data;
    });
    this.eventBus.on("set_pos_tags_filters", (pos_tags) => {
      this.pos_tags_filters = pos_tags;
    });
    this.eventBus.on("clear_pos_tags_filters", () => {
      this.pos_tags_filters.length = 0;
    });
    this.eventBus.on("update_customer", (data) => {
      this.customer = data;
    });
    
    // Setup auto-refresh for item quantities
    this.refresh_interval = setInterval(() => {
      if (this.filtered_items && this.filtered_items.length > 0) {
        this.update_cur_items_details();
      }
    }, 30000); // Refresh every 30 seconds

    // Add new event listener for currency changes
    this.eventBus.on("update_currency", (data) => {
      this.selected_currency = data.currency;
      this.exchange_rate = data.exchange_rate;

      this.eventBus.emit(
        "set_selected_currency_and_exchange_rate_for_variants",
        {
          'selected_currency': this.selected_currency,
          'exchange_rate': this.exchange_rate,
        }
      );
    });
  },

  mounted() {
    this.scan_barcoud();
    this.eventBus.on("update_invoice_type", (data) => {
      this.invoiceType = data;
    });
  },
  
  beforeUnmount() {
    this.eventBus.off("update_invoice_type");

    // Clear interval when component is destroyed
    if (this.refresh_interval) {
      clearInterval(this.refresh_interval);
    }
    
    // Call cleanup function for abort controller
    if (this.cleanupBeforeDestroy) {
      this.cleanupBeforeDestroy();
    }
    
    // Detach scanner if it was attached
    if (document._scannerAttached) {
      try {
        onScan.detachFrom(document);
        document._scannerAttached = false;
      } catch (error) {
        console.warn('Scanner detach error:', error.message);
      }
    }

    this.eventBus.off("update_currency");
  },
};
</script>

<style scoped>
.text-success {
  color: #4CAF50 !important;
}

.sleek-data-table {
  border-radius: 12px !important; /* Match Customer.vue style */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important; /* Match Customer.vue style */
  background-color: #fff !important; /* Match Customer.vue style */
  overflow: hidden !important; /* Ensures border-radius applies correctly */
}

.sleek-data-table:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important; /* Match Customer.vue style */
}

.column-settings-btn {
  position: absolute;
  right: 10px;
  top: 10px;
  z-index: 1;
}
</style>