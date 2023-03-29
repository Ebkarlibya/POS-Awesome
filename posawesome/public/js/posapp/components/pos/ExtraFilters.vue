<template>
  <div class="extra-filters-main">
    <div class="extra-filters-outside-controls" style="display: flex;">
      <v-btn
        color="primary"
        @click="openPosTags"
        class="">
        <v-badge
            color="error"
            dot
            style="position: absolute; top: 2px; left: 3px;"
            v-if="isTagsFilterActive"
          >
          </v-badge>
        <v-icon>mdi-filter-variant</v-icon>
      </v-btn>

      <v-btn
        class="mx-3"
        color="error"
        @click="clearPosTags"
        v-if="isTagsFilterActive"
      >
      <v-icon>mdi-close-thick</v-icon>
      </v-btn>
    </div>

    <v-dialog v-model="posTagsDialog" width="600">
      <v-card elevation="2" outlined shaped>
        <v-card-title>{{ __("POS Tags") }}</v-card-title>
        <!-- <v-card-actions>
          <v-btn color="primary" @click="applyPosTags">{{
            __("Clear")
          }}</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" @click="closePosTags">{{
            __("Close")
          }}</v-btn>
        </v-card-actions> -->
        <!-- <v-card-subtitle v-if="false"
          style="margin: 5px 3px 0px 3px; color: #0097a7 !important; font-size: 18px">
          {{ descriptionItem.item_name }}</v-card-subtitle>
        <br> -->

        <v-card-text>
          <v-row dense class="mx-5 mb-6">
            <v-text-field
                clearable
                v-model="search"
                append-icon="mdi-magnify"
                :label="__('Search POS Tags')"
                single-line
                hide-details
              ></v-text-field>
          </v-row>
          <v-row dense>
            <v-col class="variants-qty_controls">
              <v-btn v-for="posTag in pos_tags" :key="posTag.name" medium
                :color="posTag.selected ? 'warning' : 'white'" @click="selectPosTag(posTag)"
                class="ms-2 mb-2">
                <strong>{{ posTag.name }}</strong>
              </v-btn>

            </v-col>
          </v-row>
        </v-card-text>

        <br><br>

        <v-card-actions>
          <v-btn color="error" @click="clearPosTags">{{
            __("Clear")
          }}</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="info" @click="closePosTags">{{
            __("Ok")
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { evntBus } from '../../bus';

export default {
  data: () => ({
    posTagsDialog: false,
    pos_profile: null,
    search: '',
    _pos_tags: [],
    pos_tags: []
  }),
  methods: {
    openPosTags() {
      this.posTagsDialog = true;
    },
    closePosTags() {
      this.posTagsDialog = false;
    },
    selectPosTag(posTag) {
      posTag.selected = !posTag.selected
      this.applyPosTags()
    },
    applyPosTags() {
      evntBus.$emit("set_pos_tags_filters", this.selectedTags)
    },
    clearPosTags() {
      this.pos_tags.forEach(posTag => posTag.selected = 0)
      this.applyPosTags()
    }
  },
  computed: {
    selectedTags() {
      return this.pos_tags.filter(tag => tag.selected === true)
    },
    isTagsFilterActive(){
      return this.selectedTags.length > 0 ? true : false
    }
  },
  created: function () {
    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
      });
    });
    // fetch pos tags
    frappe.call(
      {
        method: "posawesome.api.get_pos_tags",
        callback: (r) => {
          if(r.message) {
            this._pos_tags = r.message.map(tag => {
              tag["selected"] = 0
              return tag
            })
            this.pos_tags = this._pos_tags;
          }
        }
      }
    )
  },

  watch: {
    search(value) {
      // this.clearPosTags();
      if(value) {
        this.pos_tags = [...this._pos_tags.filter(tag => tag.name.toLowerCase().includes(value.toLowerCase()))];
      } else {
        this.pos_tags = [...this._pos_tags]
      }
    }
  },
};
</script>