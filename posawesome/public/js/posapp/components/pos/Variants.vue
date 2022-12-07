<template>
  <v-row justify="center">
    <v-dialog v-model="varaintsDialog" max-width="600px">
      <v-card min-height="500px">
        <v-card-title>
          <span class="headline primary--text">Select Item</span>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            dark
            @click="insertSelectedVariantItems"
            style="margin-left: 5px; margin-right: 5px"
            >{{ __("Insert") }}</v-btn
          >
          <v-btn color="error" dark @click="close_dialog">{{
            __("Close")
          }}</v-btn>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container v-if="parentItem">
            <div v-for="attr in parentItem.attributes" :key="attr.attribute">
              <v-chip-group
                v-model="filters[attr.attribute]"
                active-class="green--text text--accent-4"
                column
              >
                <v-chip
                  v-for="value in attr.values"
                  :key="value.abbr"
                  :value="value.attribute_value"
                  outlined
                  label
                  @click="updateFiltredItems"
                >
                  {{ value.attribute_value }}
                </v-chip>
              </v-chip-group>
              <v-divider class="p-0 m-0"></v-divider>
            </div>
            <div>
              <v-row dense class="overflow-y-auto" style="max-height: 800px">
                <v-col
                  v-for="(item, idx) in filterdItems"
                  :key="idx"
                  xl="4"
                  lg="4"
                  md="4"
                  sm="4"
                  cols="12"
                  min-height="100"
                >
                  <v-card hover="hover" @click="addSelectedVariantItem(item)">
                    <v-img
                      :src="
                        item.image ||
                        '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'
                      "
                      class="white--text align-end"
                      gradient="to bottom, rgba(0,0,0,.2), rgba(0,0,0,.7)"
                      height="100px"
                    >
                      <v-card-text
                        v-text="item.item_name"
                        class="text-subtitle-2 px-1 pb-2"
                      ></v-card-text>
                    </v-img>
                    <v-card-text class="text--primary pa-1">
                      <v-row dense>
                        <v-col class="variants-qty_controls">
                          <div class="text-subtitle-2 primary--text accent-3">
                            {{ item.rate || 0 }} {{ item.currency || "" }}
                          </div>
                          <v-btn
                            color="primary"
                            @click.stop="openQtyEditDialog(item)"
                          >
                            {{ item.selectedVariantQty || 0 }}
                          </v-btn>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-model="qtyDialogShow" persistent width="350">
      <v-card elevation="2" outlined shaped>
        <v-card-title>{{ __("Set Qty") }}</v-card-title>
        <v-card-text>
          <v-row dense>
            <v-col class="variants-qty_controls">
              <v-btn
                icon
                color="secondary"
                @click.stop="qtyDialogItemValue -= 1"
                style="margin-right: 30px; margin-left: 30px"
              >
                <v-icon>mdi-minus-circle-outline</v-icon>
              </v-btn>
              <v-text-field
                :label="__('Qty')"
                hide-details="auto"
                v-model="qtyDialogItemValue"
              >
              </v-text-field>
              <v-btn
                icon
                color="secondary"
                @click.stop="qtyDialogItemValue += 1"
                style="margin-right: 30px; margin-left: 30px"
              >
                <v-icon>mdi-plus-circle-outline</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="primary"
            @click="setQty"
            :disabled="this.qtyDialogItemValue < 0"
            >{{ __("Set Qty") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn color="error" @click="qtyDialogShow = false">{{
            __("Close")
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from "../../bus";
export default {
  data: () => ({
    varaintsDialog: false,
    qtyDialogShow: false,
    qtyDialogItem: null,
    qtyDialogItemValue: 0,
    parentItem: null,
    items: null,
    filters: {},
    filterdItems: [],
  }),
  methods: {
    addSelectedVariantItem(item) {
      item.selectedVariantQty += 1;
      this.$forceUpdate();
    },
    removeSelectedVariantitem(item) {
      if (item.selectedVariantQty < 1) return;
      item.selectedVariantQty -= 1;
      this.$forceUpdate();
    },
    insertSelectedVariantItems() {
      this.filterdItems.forEach((filItem) => {
        if (filItem.selectedVariantQty) {
          for (let i = filItem.selectedVariantQty; i > 0; i--) {
            evntBus.$emit("add_item", filItem);
          }
        }
      });
      this.close_dialog();
    },
    openQtyEditDialog(item) {
      this.qtyDialogItem = item;
      this.qtyDialogItemValue = item.selectedVariantQty;
      this.qtyDialogShow = true;
    },
    setQty() {
      if (this.qtyDialogItemValue < 0) {
        return;
      }
      this.qtyDialogItem.selectedVariantQty = this.qtyDialogItemValue;
      this.qtyDialogShow = false;
      this.$forceUpdate();
    },
    close_dialog() {
      this.varaintsDialog = false;
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, "$&,");
    },
    updateFiltredItems() {
      this.$nextTick(function () {
        const values = [];
        Object.entries(this.filters).forEach(([key, value]) => {
          if (value) {
            values.push(value);
          }
        });

        if (!values.length) {
          this.filterdItems = this.variantsItems;
        } else {
          const itemsList = [];
          this.filterdItems = [];
          this.variantsItems.forEach((item) => {
            let apply = true;
            item.item_attributes.forEach((attr) => {
              if (
                this.filters[attr.attribute] &&
                this.filters[attr.attribute] != attr.attribute_value
              ) {
                apply = false;
              }
            });
            if (apply && !itemsList.includes(item.item_code)) {
              this.filterdItems.push(item);
              itemsList.push(item.item_code);
            }
          });
        }
      });
    },
  },
  computed: {
    variantsItems() {
      if (!this.parentItem) {
        return [];
      } else {
        return this.items.filter(
          (item) => item.variant_of == this.parentItem.item_code
        );
      }
    },
  },
  created: function () {
    evntBus.$on("open_variants_model", (item, items) => {
      this.varaintsDialog = true;
      this.parentItem = item || null;
      this.items = items;

      // add property to track variants insertion qty for set qty dialog
      this.items.map((it) => {
        if (it.variant_of) {
          it["selectedVariantQty"] = 0;
          return it;
        }
      });

      this.filters = {};
      this.$nextTick(function () {
        this.filterdItems = this.variantsItems;
      });
    });
  },
};
</script>

<style scoped>
.variants-qty_controls {
  display: flex;
  justify-content: space-around;
  align-items: center;
}
</style>