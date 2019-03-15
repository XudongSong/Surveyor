from jnius import autoclass

WifiManager = autoclass('android.net.wifi.WifiManager')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
activity = PythonActivity.mActivity
wifi_service = activity.getSystemService(PythonActivity.WIFI_SERVICE)


class AndroidWifi(object):
    wifi_manager = None
    wifi_scanner = None
    access_points = None

    def _get_access_points(self):
        wifi_service.startScan()
        scanned_results=WifiManager.getScanResults()
        scanned_results = scanned_results.toArray()
        access_points = []
        for access in scanned_results:
            access_point = {
                'ssid': access.SSID,
                'bssid': access.BSSID,
                'level': access.level
            }
            access_points.append(access_point)
        return access_points



