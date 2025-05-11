<template>
    <v-dialog v-model="isOpen" max-width="800px">
        <v-card>
            <v-card-title class="primary white--text">
                {{ __('Available Offers for') }} {{ itemCode }} @ {{ warehouse }}
                <v-spacer />
                <v-btn icon @click="close"><v-icon>mdi-close</v-icon></v-btn>
            </v-card-title>
            <v-card-text>
                <v-data-table :headers="headers" :items="offers" item-key="name" dense class="elevation-1 p-4"
                    :no-data-text="__('No offers found for this item')"
                >
                    <template v-slot:item.title="{ item }">
                        <strong>{{ item.title }}</strong>
                    </template>
                    <template v-slot:item.description="{ item }">
                        <small v-html="item.description"></small>
                    </template>
                    <template v-slot:item.offer="{ item }">
                        {{ item.offer }}
                    </template>
                    <template v-slot:item.valid_from="{ item }">
                        {{ item.valid_from }}
                    </template>
                    <template v-slot:item.valid_upto="{ item }">
                        {{ item.valid_upto || '-' }}
                    </template>
                    <template v-slot:item.conditions="{ item }">
                        <div v-if="item.apply_on === 'Item Code'">
                            {{ __('Applies to this item only') }}
                        </div>
                        <div v-else-if="item.apply_on === 'Item Group'">
                            {{ __('Group:') }} {{ item.item_group }}
                        </div>
                        <div v-else-if="item.apply_on === 'Brand'">
                            {{ __('Brand:') }} {{ item.brand }}
                        </div>
                        <div v-else>
                            {{ __('Applies on transaction') }}
                        </div>
                        <div v-if="item.min_qty">{{ __('Min Qty:') }} {{ item.min_qty }}</div>
                        <div v-if="item.max_qty">{{ __('Max Qty:') }} {{ item.max_qty }}</div>
                    </template>
                    <!-- <template v-slot:item.action="{ item }">
                        <v-btn small text @click="apply(item)">{{ __('Apply') }}</v-btn>
                    </template> -->
                </v-data-table>
            </v-card-text>
            <v-card-actions>
                <v-spacer />
                <v-btn text @click="refresh">{{ __('Refresh') }}</v-btn>
                <v-btn text @click="close">{{ __('Close') }}</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { evntBus } from "../../bus";

export default {
    name: 'OfferDialog',
    props: {
        itemCode: { type: String, required: true },
        warehouse: { type: String, required: true },
        pos_profile: { type: String, required: true },
    },
    data() {
        return {
            isOpen: true,
            offers: [],
            headers: [
                { text: this.__('Title'), value: 'title' },
                { text: this.__('Description'), value: 'description' },
                { text: this.__('Promo Type'), value: 'offer' },
                { text: this.__('Discount'),     value: 'discount_display' },
                { text: this.__('Qty Range'),    value: 'qty_range' },
                { text: this.__('Valid From'), value: 'valid_from' },
                { text: this.__('Valid Upto'), value: 'valid_upto' },
                { text: this.__('Conditions'), value: 'conditions' },
                // { text: this.__('Action'), value: 'action', sortable: false }
            ]
        };
    },
    watch: {
        isOpen(val) {
            if (val) {
                this.fetchOffers();
            }
        },
        itemCode() { this.fetchOffers(); },
        warehouse() { this.fetchOffers(); }
    },
    created() {
        this.fetchOffers();
    },
    methods: {
        async fetchOffers() {
            this.offers = [];
            frappe.call({
                method: "posawesome.posawesome.api.posapp.get_item_offers",
                args: {
                    item_code: this.itemCode,
                    warehouse: this.warehouse,
                    profile: this.pos_profile,
                },
                callback: r => {
                    this.offers = (r.message || []).map(o => ({
                    ...o,
                    discount_display: o.discount_percentage
                        ? `${o.discount_percentage}%`
                        : o.rate
                        ? this.currencySymbol + o.rate
                        : '-',
                    qty_range: o.min_qty || o.max_qty
                        ? `${o.min_qty || 0} – ${o.max_qty || '∞'}`
                        : '-'
                    }));
                },
                error: () => {
                    this.$root.$emit('show_message', {
                        text: this.__('Failed to load offers.'),
                        color: 'error'
                    });
                }
            });
        },
        // apply(offer) {
        //     evntBus.$emit("apply_offer_to_cart", {
        //         item_code: this.itemCode,
        //         warehouse: this.warehouse,
        //         offer
        //     });
        //     this.close();
        // },
        close() {
            this.isOpen = false;
            this.$emit("close");
        },
        refresh() {
            this.fetchOffers();
        }
    }
};
</script>

<style scoped>
.v-data-table .column-description {
    max-width: 200px;
    white-space: normal;
}
</style>