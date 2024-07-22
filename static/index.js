document.addEventListener("DOMContentLoaded", () =>{
    const postTextInput = document.querySelector(".form-group__input");
    const postImageInput = document.querySelector(".form-group__file-input");
    const postFileStatus = document.querySelector(".form-group__file-status");
    const sentBtn = document.querySelector(".form-submit__button");
    const statusDisplay = document.querySelector(".status-display"); 
    const postsDisplay = document.querySelector(".message-display"); 


    const loadPosts = () =>{
        fetch("/api/post", {
            method:"GET",
        })
        .then(response =>{
            if(!response.ok){
                postsDisplay.textContent = "載入 POST 錯誤";
                return;
            }
            return response.json();
        })
        .then(data =>{
            if(data && data.data){
                postsDisplay.innerHTML = ""; 
                data.data.forEach(post => {
                    const postText = post.text;
                    const postImage = post.image;

                    const postDisplay = document.createElement("div");
                    postDisplay.className = "message-display__block";
                    
                    const postTextDisplay = document.createElement("div");
                    postTextDisplay.className = "message-display__text";
                    postTextDisplay.textContent = postText;

                    const postImageDisplay = document.createElement("img");
                    postImageDisplay.className = "message-display__img";
                    postImageDisplay.src = postImage; 
                    
                    postsDisplay.appendChild(postDisplay);
                    postDisplay.appendChild(postTextDisplay);
                    postDisplay.appendChild(postImageDisplay);
                });
            }
        })
        .catch(error => {
            postsDisplay.textContent = "載入 POST 錯誤: " + error.message;
        });
    };
    
    const savePost = () =>{
        const request = {
            text: postTextInput.value,
            image: postImageInput.files.length > 0 ? URL.createObjectURL(postImageInput.files[0]) : ""
        };

        if (!request.text || !request.image) {
            statusDisplay.textContent = "請輸入文字或選擇圖片";
            statusDisplay.style.display = "block";
            return;
        }

        fetch("/api/post", {
            method:"POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify(request)
        })
        .then(response =>{
            if(!response.ok){
                statusDisplay.textContent = "儲存 POST 錯誤";
                statusDisplay.style.display = "block";
                return;
            }
            return response.json();
        })
        .then(data =>{
            console.log(request);
            console.log(data);
            if (data && data.success) {
                loadPosts();
                postTextInput.value = "";
                postImageInput.value = "";
                postFileStatus.textContent = "no file chosen";
                statusDisplay.style.display = "none";
            } else {
                statusDisplay.textContent = "儲存 POST 錯誤: no success";
                statusDisplay.style.display = "block";
            }
        })
        .catch(error =>{
            statusDisplay.textContent = "儲存 POST 錯誤: " + error.message;
            statusDisplay.style.display = "block";
        });  
    };

    postImageInput.addEventListener("change", () => {
        if (postImageInput.files.length > 0) {
            const fileUrl = URL.createObjectURL(postImageInput.files[0]);
            postFileStatus.textContent = fileUrl;
        } else {
            postFileStatus.textContent = "no file chosen";
        }
    });

    sentBtn.addEventListener("click", () =>{
        savePost();
    });

    loadPosts();
})