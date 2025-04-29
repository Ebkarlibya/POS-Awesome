<template>
    <v-dialog v-model="isOpen" max-width="800px">
        <v-card>
            <v-card-title class="primary white--text">
                {{ __("Select Warehouse") }}
                <v-spacer />
                <v-btn icon @click="closeDialog" :title="__('Close dialog')">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-card-title>
            <v-card-text>
                <v-data-table :headers="computedHeaders" :items="warehouseStock" item-key="warehouse"
                    class="elevation-1">
                    <template v-slot:item.warehouse="{ item }">
                        <span :class="{ 'green--text': item.main_warehouse }">
                            {{ item.warehouse }}
                        </span>
                    </template>
                    <template v-slot:item.actual_qty="{ item }">
                        {{ item.actual_qty }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn small icon @click="selectWarehouse(item)" :disabled="item.actual_qty <= 0" :title="item.actual_qty <= 0
        ? __('There is no available quantity.')
        : __('Click to add to invoice.')">
                            <v-icon>mdi-plus</v-icon>
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
                { text: this.__("Warehouse"), value: "warehouse" },
                { text: this.__("Available Qty"), value: "actual_qty" },
                { text: this.__("Actions"), value: "actions", sortable: false },
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
        selectWarehouse(chosen) {
            if (chosen.actual_qty <= 0) {
                return;
            }
            
            this.$emit("select", {
                ...this.item,
                item_selected_warehouse: chosen.warehouse,
                item_selected_warehouse_actual_qty: chosen.actual_qty
            });
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