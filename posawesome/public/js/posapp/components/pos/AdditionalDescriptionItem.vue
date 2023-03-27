<template>
    <v-row justify="center">
        <!-- additional item description dialog -->
        <v-dialog v-model="showItemDescDialog" v-if="item" persistent width="600">
            <v-card elevation="2" outlined shaped>
                <v-card-title>{{ __("Select Item Descriptions") }}</v-card-title>
                <v-card-subtitle v-if="item" style="margin: 5px 3px 0px 3px; color: #0097a7 !important; font-size: 18px">
                    {{ item.item_name }}</v-card-subtitle>
                    <v-card-subtitle>
                       {{ getTotalDescriptionsQty() }}/{{ item.qty }}
                    </v-card-subtitle>
                <br>
                <v-card-text>
                    <v-data-table :headers="tableHeaders" :items="item.additional_item_descriptions" class="elevation-1"
                        item-key="description" loading="true" :hide-default-footer="false" :items-per-page="4">
                        <template v-slot:item.description="{ item }">
                            <v-chip @click="incDescItemQty(item)">
                                {{ item.description }}
                            </v-chip>
                        </template>
                        <template v-slot:item.selected_qty="{ item }">
                            <v-chip @click="decDescItemQty(item)">
                                {{ item.selected_qty }}
                            </v-chip>
                        </template>
                    </v-data-table>
                </v-card-text>

                <v-card-actions>
                    <v-btn color="primary" @click="editDescItemNote">{{ __("Apply")
                    }}</v-btn>
                    <v-spacer></v-spacer>
                    <v-btn color="error" @click="showItemDescDialog = false">{{
                        __("Close")
                    }}</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

    </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {

    data: () => ({
        item: null,
        showItemDescDialog: false,
        itemAdditionalDescriptions: [],
        timeout: null,
        interval: null,
        pos_profile: null,
        tableHeaders: [
            {
                text: __("Description"),
                align: "start",
                sortable: false,
                value: "description",
            },
            {
                text: __("Qty"),
                align: "start",
                sortable: false,
                value: "selected_qty",
            }
        ]
    }),
    props: ['addOne', 'subtractOne'],
    watch: {},
    methods: {
        incDescItemQty(descItem) {
            if(this.getTotalDescriptionsQty() >= this.item.qty) return;

            descItem.selected_qty++;
        },
        decDescItemQty(descItem) {
            if (descItem.selected_qty > 0) {
                descItem.selected_qty--;
            }
        },
        getTotalDescriptionsQty() {
            return this.item.additional_item_descriptions.reduce((acc, cur) => acc += cur.selected_qty, 0);
        },
        editDescItemNote() {
            let descriptionText = "";
            this.item.posa_notes = "";

            for(let i = 0 ; i < this.item.additional_item_descriptions.length; i++) {
                const dItem = this.item.additional_item_descriptions[i];
                if (dItem.selected_qty > 0) {
                    descriptionText += `(${dItem.selected_qty} - ${dItem.description})\n`;
                }
            }
            this.item.posa_notes = descriptionText;
            this.showItemDescDialog = false;
        },
    },
    created: function () {
        this.$nextTick(() => {
            evntBus.$on('open_additional_item_descriptions', (item) => {
                this.showItemDescDialog = true;
                this.item = item;
            });
            evntBus.$on('register_pos_profile', (pos_profile) => {
                this.pos_profile = pos_profile;
            });
        })
    },
};
</script>
