<template>
	<v-dialog v-model="showDialog" max-width="600px" :persistent="false" @keydown.esc="closeDialog">
		<v-card>
			<v-card-title class="d-flex justify-space-between align-center">
				<span>{{ __('Column Settings') }}</span>
				<v-btn icon @click="closeDialog">
					<v-icon>mdi-close</v-icon>
				</v-btn>
			</v-card-title>
			<v-card-text>
				<v-list>
					<v-list-item v-for="header in availableHeaders" :key="header.key"
						:class="{ 'disabled-setting': !header.hideable }">
						<template v-slot:prepend>
							<v-checkbox v-model="selectedColumns[header.key]" :disabled="!header.hideable" hide-details
								class="mr-2" :label="header.title"></v-checkbox>
						</template>
						<v-list-item-title>
							<!-- {{ header.title }} -->
							<v-icon v-if="!header.hideable" small class="ml-1" title="This column cannot be hidden">
								mdi-lock
							</v-icon>
						</v-list-item-title>
						<template v-slot:append v-if="header.widthConfigurable">
							<v-menu offset-y>
								<template v-slot:activator="{ props }">
									<v-btn icon v-bind="props" size="small">
										<v-icon>mdi-arrow-expand-horizontal</v-icon>
									</v-btn>
								</template>
								<v-list density="compact">
									<v-list-item v-for="widthOption in widthOptions" :key="widthOption.value"
										@click="setColumnWidth(header.key, widthOption.value)">
										<v-list-item-title>{{ widthOption.label }}</v-list-item-title>
									</v-list-item>
								</v-list>
							</v-menu>
						</template>
					</v-list-item>
				</v-list>

				<v-divider class="my-4"></v-divider>

				<div class="d-flex align-center">
					<v-checkbox v-model="autoAdjustWidths" hide-details class="mr-2"
						:label="__('Auto-adjust column widths')"></v-checkbox>
					<v-tooltip bottom>
						<template v-slot:activator="{ on }">
							<v-icon v-on="on" small>mdi-information</v-icon>
						</template>
						<span>{{ __('Automatically adjust column widths based on content') }}</span>
					</v-tooltip>
				</div>
			</v-card-text>
			<v-card-actions>
				<v-btn color="primary" @click="saveSettings">{{ __('Save') }}</v-btn>
				<v-btn color="secondary" @click="resetToDefault">{{ __('Reset to Default') }}</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>
export default {
	props: {
		show: Boolean,
		availableHeaders: {
			type: Array,
			default: () => []
		}
	},
	data() {
		return {
			showDialog: false,
			selectedColumns: {},
			columnWidths: {},
			autoAdjustWidths: true,
			widthOptions: [
				{ label: __('Auto'), value: 'auto' },
				{ label: __('Small'), value: '100px' },
				{ label: __('Medium'), value: '200px' },
				{ label: __('Large'), value: '300px' },
				{ label: __('X-Large'), value: '400px' }
			]
		};
	},
	watch: {
		show: {
			immediate: true,
			handler(newVal) {
				this.showDialog = newVal;
			}
		},
		showDialog(newVal) {
			if (!newVal) {
				this.$emit('update:show', false);
			}
		}
	},
	methods: {
		closeDialog() {
			this.showDialog = false;
			this.$emit('update:show', false);
		},
		loadSettings() {
			// Load column visibility settings
			const savedSettings = localStorage.getItem('posawesome_column_settings');
			if (savedSettings) {
				this.selectedColumns = JSON.parse(savedSettings);
			} else {
				this.resetToDefault();
			}

			// Load column width settings
			const savedWidths = localStorage.getItem('posawesome_column_widths');
			if (savedWidths) {
				this.columnWidths = JSON.parse(savedWidths);
			}

			// Load auto-adjust setting
			const savedAutoAdjust = localStorage.getItem('posawesome_auto_adjust_widths');
			this.autoAdjustWidths = savedAutoAdjust ? JSON.parse(savedAutoAdjust) : true;
		},
		saveSettings() {
			localStorage.setItem('posawesome_column_settings', JSON.stringify(this.selectedColumns));
			localStorage.setItem('posawesome_column_widths', JSON.stringify(this.columnWidths));
			localStorage.setItem('posawesome_auto_adjust_widths', JSON.stringify(this.autoAdjustWidths));

			this.$emit('columns-changed', {
				visibility: this.selectedColumns,
				widths: this.columnWidths,
				autoAdjust: this.autoAdjustWidths
			});
			this.closeDialog();
		},
		resetToDefault() {
			this.selectedColumns = {};
			this.columnWidths = {};
			this.autoAdjustWidths = true;

			this.availableHeaders.forEach(header => {
				this.selectedColumns[header.key] = header.defaultVisible !== false;

				if (header.defaultWidth) {
					this.columnWidths[header.key] = header.defaultWidth;
				}
			});
		},
		setColumnWidth(columnKey, width) {
			this.columnWidths = {
				...this.columnWidths,
				[columnKey]: width
			};
		}
	},
	mounted() {
		this.loadSettings();
	}
};
</script>

<style scoped>
.disabled-setting {
	opacity: 0.7;
	background-color: #f5f5f5;
}
</style>
