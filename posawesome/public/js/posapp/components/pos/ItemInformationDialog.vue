<template>
    <v-dialog v-model="isOpen" max-width="800px">
        <v-card>
            <v-card-title class="primary white--text">
                {{ __("Item Information") }}
                <v-spacer />
                <v-btn icon @click="closeDialog" :title="__('Close dialog')">
                    <v-icon>mdi-close</v-icon>
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
                                <div class="text-h5 primary--text">
                                    {{ currencySymbol(item.currency) }}{{ formatCurrency(item.rate) }}
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
                        <v-btn small icon @click="selectWarehouse(item)" :disabled="item.actual_qty <= 0"
                            :title="item.actual_qty <= 0 ? __('Out of stock') : __('Add from this warehouse')">
                            <v-icon>mdi-cart-plus</v-icon>
                        </v-btn>
                        <v-btn small icon
                              @click="openOffers(item)"
                              :title="__('Show Offers for this item')">
                            <v-icon>mdi-tag</v-icon>
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

            this.$emit("select", {
                ...this.item,
                item_selected_warehouse: chosen.warehouse,
                item_selected_warehouse_actual_qty: chosen.actual_qty
            });
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