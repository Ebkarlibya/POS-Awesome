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