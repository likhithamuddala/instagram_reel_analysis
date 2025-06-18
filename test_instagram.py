import requests

headers = {
    "cookie": "71333977052%3AovyhBQWTygaU2h%3A15%3AAYenjn_NxOcRcio2UzUe_VKhAw5KikLPJ-Mdn92oJw; X4z0eYBMDv94ccpZqo2v1frEDEqOCU77;",
    "user-agent": "Mozilla/5.0"
}

# Use any valid reel shortcode (not full URL)
url = "https://www.instagram.com/api/v1/media/DK9oElPvECT/info/"

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response Text:")
print(response.text)
