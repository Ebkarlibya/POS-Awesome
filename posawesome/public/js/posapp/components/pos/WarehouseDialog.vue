<template>
    <v-dialog v-model="isOpen" width="800">
        <v-card>
            <v-card-title class="d-flex justify-space-between align-center primary white--text">
                {{ __("Select Warehouse") }}
                <v-btn
                    icon
                    size="small"
                    density="compact"
                    @click="closeDialog"
                    :title="__('Close dialog')"
                >
                    <v-icon size="20">mdi-close</v-icon>
                </v-btn>
            </v-card-title>
            <v-card-text>
                <!-- Add item information section -->
                <v-row class="mb-4">
                    <v-col cols="12">
                        <v-card class="pa-3" variant="outlined">
                            <v-row>
                                <v-col cols="3">
                                    <v-img :src="item.image || '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'"
                                        class="elevation-2" height="80" contain></v-img>
                                </v-col>
                                <v-col cols="9">
                                    <h3 class="text-h6 primary--text">{{ item.item_name }}</h3>
                                    <div class="text-subtitle-2">{{ item.item_code }}</div>
                                    <div class="d-flex flex-column align-start mt-1">
                                        <span class="text-body-1 text-primary">
                                            {{ currencySymbol(pos_profile.currency) || "" }}
                                            {{ format_currency(item.rate, pos_profile.currency, 4) }}
                                        </span>
                                        <span v-if="pos_profile.posa_allow_multi_currency && selected_currency !== pos_profile.currency" 
                                              class="text-body-1 text-success">
                                            {{ currencySymbol(selected_currency) || "" }}
                                            {{ format_currency(getConvertedRate(item), selected_currency, 4) }}
                                        </span>
                                    </div>
                                </v-col>
                            </v-row>
                        </v-card>
                    </v-col>
                </v-row>

                <v-data-table :headers="computedHeaders" :items="warehouseStock" item-key="warehouse"
                    class="elevation-1">
                    <template v-slot:item.warehouse="{ item }">
                        <span :class="{ 'green--text': item.main_warehouse }">
                            {{ item.warehouse }}
                            <v-icon small v-if="item.main_warehouse">mdi-home</v-icon>
                        </span>
                    </template>
                    <template v-slot:item.actual_qty="{ item }">
                        {{ item.actual_qty }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn
                            icon
                            size="large"
                            density="compact"
                            @click="selectWarehouse(item)"
                            :disabled="item.actual_qty <= 0"
                            :title="item.actual_qty <= 0
                                    ? __('There is no available quantity.')
                                    : __('Click to add to invoice.')"
                        >
                        <v-icon size="28">mdi-plus</v-icon>
                        </v-btn>
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import format from "../../format";

export default {
    mixins: [format],
    props: {
        item: Object,
        warehouses: Array,
        main_warehouse: String,
        pos_profile: Object,
        selected_currency: String,
        exchange_rate: Number,
    },
    data() {
        return {
            isOpen: true,
            warehouseStock: [],
        };
    },
    computed: {
        computedHeaders() {
            return [
                { title: this.__("Warehouse"), key: "warehouse" },
                { title: this.__("Available Qty"), key: "actual_qty" },
                { title: this.__("Actions"), key: "actions", sortable: false },
            ];
        },
    },
    created() {
        this.fetchStockQuantities();
    },
    methods: {
        getConvertedRate(item) {
            if (!item.rate) return 0;
            if (!this.exchange_rate) return item.rate;

            const convertedRate = item.rate / this.exchange_rate;
            return this.flt(convertedRate, 4);
        },

        format_currency(value, currency, precision) {
            if (!value) return '0';
            
            let valueStr = value.toString();
            if (valueStr.includes('.')) {
                return flt(value, 4).toString();
            }
            return valueStr;
        },

        currencySymbol(currency) {
            return get_currency_symbol(currency);
        },

        fetchStockQuantities() {
            frappe.call({
                method: "posawesome.posawesome.api.posapp.get_item_warehouse_stock",
                args: {
                    item_code: this.item.item_code,
                    warehouses: this.warehouses.map((w) => w.warehouse),
                    main_warehouse: this.main_warehouse,
                },
                callback: (result) => {
                    this.warehouseStock = result.message || [];
                },
            });
        },
        
        selectWarehouse(chosen) {
            if (chosen.actual_qty <= 0) {
                return;
            }
            
            // Prepare the item with currency conversion
            let itemToAdd = {
                ...this.item,
                item_selected_warehouse: chosen.warehouse,
                item_selected_warehouse_actual_qty: chosen.actual_qty
            };
            
            // Ensure UOMs are initialized
            if (!itemToAdd.item_uoms || itemToAdd.item_uoms.length === 0) {
                itemToAdd.item_uoms = [{ uom: itemToAdd.stock_uom, conversion_factor: 1.0 }];
            }
            
            // Convert rate if multi-currency is enabled
            if (this.pos_profile.posa_allow_multi_currency && 
                this.selected_currency !== this.pos_profile.currency) {
                // Store original rate as base_rate
                itemToAdd.base_rate = itemToAdd.rate;
                itemToAdd.base_price_list_rate = itemToAdd.price_list_rate;
                
                // Set converted rates
                itemToAdd.rate = this.getConvertedRate(itemToAdd);
                itemToAdd.price_list_rate = this.getConvertedRate(itemToAdd);
                
                // Set currency
                itemToAdd.currency = this.selected_currency;
            }

            // Set default quantity
            if (!itemToAdd.qty || itemToAdd.qty === 1) {
                itemToAdd.qty = 1;
            }
            
            this.$emit("select", itemToAdd);
            this.closeDialog();
        },
        
        closeDialog() {
            this.isOpen = false;
            this.$emit("close");
        },
    },
    watch: {
        isOpen(val) {
            if (!val) {
                this.$emit("close");
            }
        }
    }
};
</script>