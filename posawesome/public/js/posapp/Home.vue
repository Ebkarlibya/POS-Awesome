<template>
  <v-app class="container1">
    <v-main>
      <Navbar @changePage="setPage($event)"></Navbar>
      <keep-alive>
        <component v-bind:is="page" class="mx-4 md-4"></component>
      </keep-alive>
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue';
import POS from './components/pos/Pos.vue';

frappe.pos_show_alert = frappe.toast = function (message, actions = {}) {
  let indicator_icon_map = {
    orange: "solid-warning",
    yellow: "solid-warning",
    blue: "solid-info",
    green: "solid-success",
    red: "solid-error",
  };

  if (typeof message === "string") {
    message = {
      message: message,
    };
  }

  if (!$("#dialog-container").length) {
    $('<div id="dialog-container"><div id="alert-container"></div></div>').appendTo("body");
  }

  let icon;
  if (message.indicator) {
    icon = indicator_icon_map[message.indicator.toLowerCase()] || "solid-" + message.indicator;
  } else {
    icon = "solid-info";
  }

  const indicator = message.indicator || "red";

  const div = $(`
		<div class="alert desk-alert ${indicator}" role="alert">
			<div class="alert-message-container">
				<div class="alert-title-container">
					<div>${frappe.utils.icon(icon, "lg")}</div>
					<div class="alert-message">${message.message}</div>
				</div>
				<div class="alert-subtitle">${message.subtitle || ""}</div>
			</div>
			<div class="alert-body" style="display: none"></div>
			<a class="close">${frappe.utils.icon("close-alt")}</a>
		</div>
	`);

  div.hide().appendTo("#alert-container").show();

  if (message.body) {
    div.find(".alert-body").show().html(message.body);
  }

  div.find(".close, button").click(function () {
    div.addClass("out");
    setTimeout(() => div.remove(), 800);
    return false;
  });

  Object.keys(actions).map((key) => {
    div.find(`[data-action=${key}]`).on("click", actions[key]);
  });

  return div;
};

export default {
  data: function () {
    return {
      page: 'POS',
      posAlert: null
    };
  },
  components: {
    Navbar,
    POS,
  },
  methods: {
    setPage(page) {
      this.page = page;
    },
    remove_frappe_nav() {
      this.$nextTick(function () {
        $('.page-head').remove();
        $('.navbar.navbar-default.navbar-fixed-top').remove();
      });
    },
    async checkConnection() {
      try {
        let timestamp = Date.now()
        // let res = await fetch(`https://cdn.jsdelivr.net/npm/ci-info@3.8.0/LICENSE?timestamp=${timestamp}`)
        let res = await frappe.call({ method: "posawesome.api.check_connection" })

        if (this.posAlert) {
          this.posAlert.remove()
        }

        if (res.message) {
          this.onLine = true
          let posAlert = frappe.pos_show_alert(__("POS Plus: <strong>Online</strong>."))
          setTimeout(() => posAlert.remove(), 3000)
        }
        else {
          if (this.posAlert) {
            this.posAlert.remove()
          }
          this.posAlert = frappe.pos_show_alert({
            message: __("POS Plus: <string>Offline!</string>, Internet is Required for the POS to work properly !"),
            title: __("ETMS POS: Connectivity"),
            indicator: "red"
          })
        }
      } catch (e) {
        this.posAlert = frappe.pos_show_alert({
          message: __("POS Plus: <string>Offline!</string>, Internet is Required for the POS to work properly !"),
          title: __("ETMS POS: Connectivity"),
          indicator: "red"
        })
      }
    }
  },
  mounted() {
    this.remove_frappe_nav();
    setTimeout(() => {
      this.checkConnection()

      setInterval(() => {
        this.checkConnection()
      }, 60000);
    }, 3000)

  },
  updated() { },
  created: function () {
    setTimeout(() => {
      this.remove_frappe_nav();
      frappe.realtime.on("emp_cups_waiting_printers_jobs", async (data) => {
        let jobsCount = 0
        let printers = ""

        for (let printer in data) {
          printers += `${printer}\n`
          for (job in data[printer]) {
            jobsCount += 1
          }
        }

        if (jobsCount < 1) return

        const clearText = __('Clear')
        const keepText = __('Keep')
        let result = await this.$vToastify.prompt({
          body: __(`
            There are ({}) Pending Print Jobs, Clear All?<br>\n
            
            Printers:<br>\n
            {}
            `, [jobsCount, printers]),
          answers: { Clear: true, Keep: false }
        })
        if (result) {
          frappe.call({
            method: "etms_multi_printers.api.clear_all_jobs",
            args: {},
            callback: function (r) {
              console.log(r.message);
            }
          })
        }
      })
    }, 1000);
  },
};
</script>

<style scoped>
.container1 {
  margin-top: 0px;
}
</style>