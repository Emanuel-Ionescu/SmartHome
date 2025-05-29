function OpenRoomMenu() {
    document.getElementById("room_nav").style.width = "100%";
}
  
function CloseRoomMenu() {
    document.getElementById("room_nav").style.width = "0%";
}

function Bulb_Select(val)
{
    fetch('/bulb_select', {
        method: 'POST', 
        headers: {'Content-Type':'application/json'}, 
        body:JSON.stringify({value:val})
    })
    document.getElementById('bulb_dropdown_display').innerHTML = val
}

function Bulb_buttonClick(rm, val)
{
    fetch('/bulb_bttn_set', {
        method: 'POST', 
        headers: {'Content-Type':'application/json'}, 
        body:JSON.stringify({
            room : rm,
            bulb : document.getElementById('bulb_dropdown_display').innerHTML,
            value:val
        })
    })
}

function Camera_Move(rm, dir) 
{
    fetch('/camera_move', {
        method: 'POST', 
        headers: {'Content-Type':'application/json'}, 
        body:JSON.stringify({
            room     :rm, 
            direction:dir
        })
    }) 
}