<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style lang="scss">
	* {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	page {
		background: #eaf1ff;
		font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
		color: #2f4672;
		font-size: 14px;
		line-height: 1.6;
	}
</style>
