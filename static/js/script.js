async function twitter_analytics(){
    topic = document.getElementById("name").value;
    payload = {topic}
    response = await fetch("/twitter_analysis",{
        method : "POST",
        headers : {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)


    });
    const result = response.json()
    console.log(result)
    document.getElementById("output").innerText = result

}