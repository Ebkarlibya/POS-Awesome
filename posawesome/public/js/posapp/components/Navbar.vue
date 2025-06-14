<template>
  <nav>
    <ListInvoices></ListInvoices>
    <ListOrders></ListOrders>

    <v-app-bar app flat height="56" color="white" class="border-bottom">
      <v-app-bar-nav-icon
        ref="navIcon"
        @click="handleNavClick"
        class="text-secondary"
      />
      <v-img
        :src="companyImg"
        :alt="company"
        max-width="32"
        class="mx-2"
      />
      <v-toolbar-title
        @click="goDesk"
        class="text-h6 font-weight-bold text-primary"
        style="cursor: pointer;"
      >
        <span class="font-weight-light me-1">{{ company }}</span>
        <span>POS</span>
      </v-toolbar-title>

      <v-spacer />
      <v-btn style="cursor: unset; text-transform: none;" variant="text" color="primary">
        {{ posProfile.name }}
      </v-btn>
      <v-menu offset-y offset-x :min-width="200">
        <template #activator="{ props }">
          <v-btn v-bind="props" color="primary" theme="dark" variant="text" class="user-menu-btn">
            {{ __('Menu') }}
            <v-icon right>mdi-menu-down</v-icon>
          </v-btn>
        </template>
        <v-card class="user-menu-card" tile>
          <v-list dense class="user-menu-list">
            <v-list-item
              @click="openCloseShift"
              v-if="!posProfile.posa_hide_closing_shift"
              class="user-menu-item"
            >
              <v-list-item-icon>
                <v-icon>mdi-content-save-move-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-title>
                {{ __("Close Shift") }}
              </v-list-item-title>
            </v-list-item>
            <v-list-item
              @click="printLastInvoice"
              v-if="posProfile.posa_allow_print_last_invoice && lastInvoiceId"
              class="user-menu-item"
            >
              <v-list-item-icon>
                <v-icon>mdi-printer</v-icon>
              </v-list-item-icon>
              <v-list-item-title>
                {{ __("Print Last Invoice") }}
              </v-list-item-title>
            </v-list-item>
            <v-divider class="my-2" />

            <v-list-item
              @click="openClosingShiftsList"
              class="user-menu-item"
            >
              <v-list-item-icon>
                <v-icon>mdi-menu</v-icon>
              </v-list-item-icon>
              <v-list-item-title>
                {{ __("Previous Closing Shifts") }}
              </v-list-item-title>
            </v-list-item>

            <v-list-item
              @click="openDesk"
              class="user-menu-item"
            >
              <v-list-item-icon>
                <v-icon>mdi-menu</v-icon>
              </v-list-item-icon>
              <v-list-item-title>
                {{ __("Desk") }}
              </v-list-item-title>
            </v-list-item>

                <!-- <v-divider class="my-0"></v-divider> -->

                <!-- List Invoices to print -->
                <!-- <v-list-item @click="openInvoicesList">
                  <v-list-item-icon>
                    <v-icon>mdi-menu</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{
                      __("Invoices List")
                    }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item> -->

                <!-- List orders to print -->
                <!-- <v-list-item @click="openOrdersList">
                  <v-list-item-icon>
                    <v-icon>mdi-menu</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{
                      __("Orders List")
                    }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item> -->

                <v-divider class="my-2" />
            <v-list-item @click="logOut" class="user-menu-item">
              <v-list-item-icon>
                <v-icon>mdi-logout</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ __("Logout") }}</v-list-item-title>
            </v-list-item>
            <v-list-item @click="goAbout" class="user-menu-item">
              <v-list-item-icon>
                <v-icon>mdi-information-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ __("About") }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      :mini-variant="mini"
      expand-on-hover
      app
      class="drawer-custom"
      @mouseleave="handleMouseLeave"
      width="220"
    >
      <div v-if="!mini" class="drawer-header">
        <v-avatar size="40"><v-img :src="companyImg" alt="Company logo" /></v-avatar>
        <span class="drawer-company">{{ company }}</span>
        <v-btn icon @click.stop="mini = true">
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
      </div>

      <div v-else class="drawer-header-mini">
        <v-avatar size="40"><v-img :src="companyImg" alt="Company logo" /></v-avatar>
      </div>
      <v-divider />
      <v-list dense nav>
        <v-list-item-group v-model="item" active-class="active-item">
          <v-list-item
            v-for="i in items"
            :key="i.text"
            @click="changePage(i.text)"
            class="drawer-item"
          >
            <v-list-item-icon>
              <v-icon class="drawer-icon">{{ i.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content v-if="!mini">
              <v-list-item-title class="drawer-item-title">{{ i.text }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-snackbar v-model="snack" :timeout="5000" :color="snackColor" location="top right">
      {{ snackText }}
    </v-snackbar>
    <v-dialog v-model="freeze" persistent max-width="290">
      <v-card>
        <v-card-title class="text-h5">
          {{ freezeTitle }}
        </v-card-title>
        <v-card-text>{{ freezeMsg }}</v-card-text>
      </v-card>
    </v-dialog>
  </nav>
</template>

<script>
import ListInvoices from "./pos/ListInvoices.vue";
import ListOrders from "./pos/ListOrders.vue";

export default {
  name: 'NavBar',
  components: { ListInvoices, ListOrders },

  data() {
    return {
      drawer: false,
      mini: true,
      item: 0,
      items: [{ text: "POS", icon: "mdi-network-pos" }],
      company: '',
      companyImg: '/assets/erpnext/images/erpnext-logo.svg',
      posProfile: {},
      lastInvoiceId: null,
      snack: false,
      snackColor: "",
      snackText: "",
      pos_settings_panel:"",
      freeze: false,
      freezeTitle: "",
      freezeMsg: ""
    };
  },
  methods: {
    handleNavClick() {
      this.drawer = true;
      this.mini = false;
    },
    handleMouseLeave() {
      if (!this.drawer) return;
      clearTimeout(this._closeTimeout);
      this._closeTimeout = setTimeout(() => {
        this.drawer = false;
        this.mini = true;
      }, 250);
    },
    changePage(key) {
      this.eventBus.emit("changePage", key);
    },
    goDesk() {
      frappe.set_route("/");
      location.reload();
    },
    goAbout() {
      const win = window.open("https://ebkar.ly/", "_blank");
      win.focus();
    },
    openClosingShiftsList() {
      const win = window.open("/app/pos-closing-shift", "_blank");
      win.focus();
    },
    openInvoicesList() {
      this.eventBus.emit("open_invoices_list");
    },
    openOrdersList() {
      this.eventBus.emit("open_orders_list");
    },
    openDesk() {
      const win = window.open("/app", "_blank");
      win.focus();
    },
    close_shift_dialog() {
      this.eventBus.emit("open_closing_dialog");
    },
    showMessage(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.title;
    },
    logOut() {
      frappe.call({
        method: 'logout',
        callback: r => {
          if (!r.exc) {
            frappe.set_route('/app/home');
            location.reload();
          }
        }
      });
    },
    openCloseShift() {
      this.eventBus.emit('open_closing_dialog');
    },
    printLastInvoice() {
      if (!this.lastInvoiceId) return;
      const pf = this.posProfile.print_format_for_online || this.posProfile.print_format;
      const noLetterHead = this.posProfile.letter_head || 0;
      const url = `${frappe.urllib.get_base_url()}/printview?doctype=Sales%20Invoice&name=${this.lastInvoiceId}` +
        `&trigger_print=1&format=${pf}&no_letterhead=${noLetterHead}`;
      const win = window.open(url, '_blank');
      win.addEventListener('load', () => win.print(), { once: true });
    },
  },
  created: function () {
    this.$nextTick(function () {
      this.eventBus.on("show_message", (data) => {
        this.showMessage(data);
      });
      this.eventBus.on("set_company", (data) => {
        this.company = data.name || "POS PLUS";
        this.companyImg = data.company_logo
          ? data.company_logo
          : this.companyImg;
        // this.company = data.name;
        // this.companyImg = data.company_logo
        //   ? data.company_logo
        //   : this.companyImg;
      });
      this.eventBus.on("register_pos_profile", async (data) => {
        company_logo = await frappe.db.get_value(
          "Company",
          data.pos_profile.company,
          ["company_logo"]
        );
        company = data.pos_profile.company || "POS PLUS";
        companyImg =
          company_logo.message.company_logo ||
          "/assets/erpnext/images/erpnext-logo.svg";

        this.posProfile = data.pos_profile;
        this.pos_settings_panel = data.pos_settings_panel
        const payments = { text: "Payments", icon: "mdi-cash-register" };
        if (
          this.posProfile.posa_use_pos_awesome_payments &&
          this.items.length !== 2
        ) {
          this.items.push(payments);
        }
        this.items.push({ text: "Orders", icon: "mdi-salesforce" });
        this.items.push({
          text: "Invoices",
          icon: "mdi-cash",
        });
      });
      this.eventBus.on("set_last_invoice", (data) => {
        this.lastInvoiceId = data;
      });
      this.eventBus.on("freeze", (data) => {
        this.freeze = true;
        this.freezeTitle = data.title;
        this.freezeMsg = data.msg;
      });
      this.eventBus.on("unfreeze", () => {
        this.freeze = false;
        this.freezTitle = "";
        this.freezeMsg = "";
      });
    });
  },
};
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid #e0e0e0;
}
.text-secondary {
  color: rgba(0, 0, 0, 0.6) !important;
}
.drawer-custom {
  background-color: #fafafa;
  transition: all 0.3s ease-out;
}
.drawer-header {
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 16px;
}
.drawer-header-mini {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 64px;
}
.drawer-company {
  margin-left: 12px;
  flex: 1;
  font-weight: 500;
  font-size: 1rem;
  color: #424242;
}
.drawer-icon {
  font-size: 24px;
  color: #1976d2;
}
.drawer-item-title {
  margin-left: 8px;
  font-weight: 500;
  color: #424242;
}
.v-list-item:hover {
  background-color: rgba(25, 118, 210, 0.1) !important;
}
.active-item {
  background-color: rgba(25, 118, 210, 0.2) !important;
}
.user-menu-btn {
  text-transform: none;
  padding: 4px 12px;
  font-weight: 500;
}
.user-menu-card {
  border-radius: 8px;
  overflow: hidden;
}
.user-menu-list {
  padding-top: 8px;
  padding-bottom: 8px;
}
.user-menu-item {
  padding: 10px 16px;
}
.user-menu-item .v-list-item-icon {
  min-width: 36px;
}
.user-menu-card .v-divider {
  margin: 8px 0;
}
</style>
