//非同期通信でデータを送信するためのJavaScriptコード

// POSTリクエストでデータを送信する例
function submitData() {
  const userData = {
      name: document.getElementById('name').value,
      email: document.getElementById('email').value
  };

  fetch('/process-data', {
      method: 'POST',  // POSTリクエスト
      headers: {
          'Content-Type': 'application/json'  // JSON形式で送信
      },
      body: JSON.stringify(userData)  // データをJSON形式で送信
  })
  .then(response => response.json())  // サーバーからのレスポンスをJSONとして処理
  .then(data => {
      console.log(data);  // サーバーからのレスポンスデータを表示
  })
  .catch(error => {
      console.error('Error:', error);  // エラー処理
  });
}