<template>
    <v-dialog v-model="isOpen" width="800">
        <v-card>
            <v-card-title class="d-flex justify-space-between align-center primary white--text">
                {{ __("Item Information") }}
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
                <v-row class="mb-4">
                    <v-col cols="4">
                        <v-img :src="item.image || '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'"
                            class="elevation-2" height="200" contain></v-img>
                    </v-col>
                    <v-col cols="8">
                        <h1 class="text-h4 primary--text">{{ item.item_name }}</h1>
                        <div class="text-subtitle-1 mb-2">{{ item.item_code }}</div>
                        <v-divider class="my-3"></v-divider>

                        <div class="text-body-1 mb-2" v-if="item.description" v-html="item.description"></div>

                        <v-row dense>
                            <v-col cols="6">
                                <div class="text-caption grey--text">{{ __("Price") }}</div>
                                <div class="d-flex flex-column align-start">
                                    <span class="text-h5 text-primary" style="white-space: normal; word-break: break-word;">
                                        {{ currencySymbol(pos_profile.currency) || "" }}
                                        {{ format_currency(item.rate, pos_profile.currency, 4) }}
                                    </span>
                                    <span v-if="pos_profile.posa_allow_multi_currency && selected_currency !== pos_profile.currency" 
                                          class="text-h5 text-success" style="white-space: normal; word-break: break-word;">
                                        {{ currencySymbol(selected_currency) || "" }}
                                        {{ format_currency(getConvertedRate(item), selected_currency, 4) }}
                                    </span>
                                </div>
                            </v-col>
                            <v-col cols="6">
                                <div class="text-caption grey--text">{{ __("Stock UOM") }}</div>
                                <div class="text-h6">{{ item.stock_uom }}</div>
                            </v-col>
                        </v-row>

                        <v-row dense v-if="item.brand">
                            <v-col cols="12">
                                <div class="text-caption grey--text">{{ __("Brand") }}</div>
                                <div class="text-body-1">{{ item.brand }}</div>
                            </v-col>
                        </v-row>
                    </v-col>
                </v-row>

                <v-data-table :headers="computedHeaders" :items="warehouseStock" item-key="warehouse"
                    class="elevation-1" dense>
                    <template v-slot:item.warehouse="{ item }">
                        <span :class="{ 'green--text font-weight-bold': item.main_warehouse }">
                            {{ item.warehouse }}
                            <v-icon small v-if="item.main_warehouse">mdi-home</v-icon>
                        </span>
                    </template>
                    <template v-slot:item.actual_qty="{ item }">
                        <span :class="getStockClass(item.actual_qty)">
                            {{ item.actual_qty }}
                        </span>
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn
                            icon
                            size="large"
                            density="compact"
                            @click="selectWarehouse(item)"
                            :disabled="item.actual_qty <= 0"
                            :title="item.actual_qty <= 0
                                    ? __('Out of stock')
                                    : __('Add from this warehouse')"
                        >
                            <v-icon size="28">mdi-cart-plus</v-icon>
                        </v-btn>
                        <v-btn
                            icon
                            size="large"
                            density="compact"
                            @click="openOffers(item)"
                            :title="__('Show Offers for this item')"
                            class="m-2"
                        >
                            <v-icon size="28">mdi-tag</v-icon>
                        </v-btn>
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import format from "../../format";
// import { evntBus } from "../../bus";

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
                { title: this.__("Available Qty"), key: "actual_qty", align: 'center' },
                { title: this.__("Actions"), key: "actions", sortable: false, align: 'center' },
            ];
        },
    },
    created() {
        this.fetchStockQuantities();
    },
    methods: {
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

        getStockClass(qty) {
            return {
                'red--text': qty <= 0,
                'orange--text': qty > 0 && qty <= 10,
                'green--text': qty > 10
            };
        },

        selectWarehouse(chosen) {
            if (chosen.actual_qty <= 0) return;

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

        openOffers(chosen) {
            this.eventBus.emit("show_offers_dialog", {
                item_code: this.item.item_code,
                warehouse: chosen.warehouse,
            });
        },

        closeDialog() {
            this.isOpen = false;
            this.$emit("close");
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
        
        getConvertedRate(item) {
            if (!item.rate) return 0;
            if (!this.exchange_rate) return item.rate;

            const convertedRate = item.rate / this.exchange_rate;
            return this.flt(convertedRate, 4);
        },

        currencySymbol(currency) {
            return get_currency_symbol(currency);
        },
    },
    watch: {
        isOpen(val) {
            if (!val) this.$emit("close");
        }
    }
};
</script>

<style scoped>
.v-img {
    border-radius: 8px;
    border: 2px solid #eee;
}

.text-h4 {
    word-break: break-word;
}
</style>