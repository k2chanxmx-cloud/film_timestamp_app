const photos = document.getElementById("photos");
const preview = document.getElementById("preview");
const btn = document.getElementById("btn");
const result = document.getElementById("result");
const resultArea = document.getElementById("resultArea");
const statusText = document.getElementById("status");
const dateInput = document.getElementById("date");

dateInput.value = new Date().toISOString().slice(0, 10);

photos.addEventListener("change", () => {
  preview.innerHTML = "";
  result.innerHTML = "";
  resultArea.classList.add("hidden");
  statusText.textContent = "";

  const files = Array.from(photos.files);

  files.slice(0, 12).forEach(file => {
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    preview.appendChild(img);
  });

  if (files.length > 12) {
    const more = document.createElement("div");
    more.className = "more-count";
    more.textContent = `+${files.length - 12}`;
    preview.appendChild(more);
  }
});

btn.addEventListener("click", async () => {
  if (!photos.files.length) {
    statusText.textContent = "写真を選択してください";
    return;
  }

  if (!dateInput.value) {
    statusText.textContent = "日付を入力してください";
    return;
  }

  const fd = new FormData();

  Array.from(photos.files).forEach(file => {
    fd.append("photos", file);
  });

  fd.append("date", dateInput.value);
  fd.append("format", document.getElementById("format").value);

  btn.disabled = true;
  btn.textContent = "加工中...";
  statusText.textContent = "写真に日付を入れています";
  result.innerHTML = "";
  resultArea.classList.add("hidden");

  try {
    const res = await fetch("/process", {
      method: "POST",
      body: fd
    });

    const data = await res.json();

    if (!data.ok) {
      throw new Error("加工に失敗しました");
    }

    data.images.forEach(url => {
      const card = document.createElement("div");
      card.className = "result-card";

      const img = document.createElement("img");
      img.src = url;

      const a = document.createElement("a");
      a.href = url;
      a.download = "film_stamp.jpg";
      a.textContent = "画像を保存";
      a.className = "save-btn";

      card.appendChild(img);
      card.appendChild(a);
      result.appendChild(card);
    });

    statusText.textContent = "完成しました";
    resultArea.classList.remove("hidden");

  } catch (err) {
    statusText.textContent = err.message || "通信エラーが発生しました";
  } finally {
    btn.disabled = false;
    btn.textContent = "タイムスタンプを入れる";
  }
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js");
}