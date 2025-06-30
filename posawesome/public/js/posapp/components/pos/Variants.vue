<template>
  <v-dialog v-model="variantsDialog" max-width="700" scrollable>
    <v-card min-height="500">
      <v-toolbar color="primary" density="compact">
        <v-toolbar-title class="text-h5">{{ frappe._('Select Item') }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" @click="close_dialog"></v-btn>
      </v-toolbar>

      <v-card-text class="pa-4">
        <div v-if="parentItem">
          <div v-for="attr in parentItem.attributes" :key="attr.attribute" class="mb-2 d-flex align-center">
            <div class="text-subtitle-1 mr-2" style="min-width: 120px">{{ attr.attribute }}:</div>
            <v-chip-group 
              v-model="filters[attr.attribute]"
              selected-class="bg-primary"
              @update:model-value="updateFilteredItems"
            >
              <v-chip
                v-for="value in attr.values"
                :key="value.abbr"
                :value="value.attribute_value"
                variant="outlined"
                size="small"
                filter
              >
                {{ value.attribute_value }}
              </v-chip>
            </v-chip-group>
          </div>
          <v-divider class="my-3"></v-divider>

          <v-row class="overflow-y-auto" style="max-height: 400px">
            <v-col
              v-for="(item, idx) in filteredItems"
              :key="idx"
              cols="6"
              sm="4"
              md="3"
            >
              <v-card 
                border
                hover
                @click="add_item(item)"
                class="h-100"
              >
                <v-img
                  :src="item.image || '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'"
                  cover
                  height="120"
                  gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                >
                  <v-card-title class="text-subtitle-2 text-white px-2 pb-1">
                    {{ item.item_name }}
                  </v-card-title>
                </v-img>
                
                <v-card-text class="pa-2 text-center">
                  <div class="text-caption text-primary">
                    {{ formatCurrency(item.rate || 0) }} {{ item.currency || '' }}
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data: () => ({
    variantsDialog: false,
    parentItem: null,
    items: null,
    filters: {},
    filteredItems: [],
  }),

  computed: {
    variantsItems() {
      if (!this.parentItem || !this.items) return [];
      return this.items.filter(
        item => item.variant_of === this.parentItem.item_code
      );
    }
  },

  methods: {
    close_dialog() {
      this.variantsDialog = false;
      this.filters = {};
    },
    
    formatCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    
    updateFilteredItems() {
      let items = [...this.variantsItems];
      
      for (const [attribute, selectedValue] of Object.entries(this.filters)) {
        if (selectedValue) {
          items = items.filter(item => 
            item.item_attributes.some(attr => 
              attr.attribute === attribute && 
              attr.attribute_value === selectedValue
            )
          );
        }
      }
      
      this.filteredItems = items;
    },
    
    add_item(item) {
      this.eventBus.emit('add_item', item);
      this.close_dialog();
    }
  },

  created: function () {
    this.eventBus.on('open_variants_model', (data) => {
      this.variantsDialog = true;
      this.parentItem = data.item || null;
      this.items = data.items;
      this.filters = {};
      this.filteredItems = this.variantsItems;
    });
  },

  beforeUnmount() {
    this.eventBus.off('open_variants_model');
  },
};
</script>

<style scoped>
.v-card {
  transition: all 0.2s ease;
  cursor: pointer;
}

.v-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.bg-primary {
  background-color: rgb(var(--v-theme-primary)) !important;
  color: white !important;
}

.d-flex + .d-flex {
  margin-top: 12px;
}
</style>