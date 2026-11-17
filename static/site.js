let services = [];
let currentCategory = "all";

const CATEGORY_NAMES = {
    ai: "AI Assistants",
    cdn: "CDN & Infrastructure",
    dating: "Dating",
    gambling: "Gambling",
    gaming: "Gaming",
    hosting: "Cloud & Hosting",
    messenger: "Messaging",
    privacy: "Privacy & Security",
    shopping: "Shopping",
    social_network: "Social Networks",
    software: "Software",
    streaming: "Streaming Media"
};

async function load() {

    const response =
        await fetch("/api/services");

    const data =
        await response.json();

    services =
        data.services;

    renderShell(data);

    buildCategories();

    draw();
}

function categoryLabel(category){

    return (
        CATEGORY_NAMES[category] ||
        category
            .replaceAll('_', ' ')
            .replace(/\b\w/g, c => c.toUpperCase())
    );
}

function renderShell(data){

    document.getElementById("app").innerHTML = `
        <div class="header">

            <h1>Blocked Services</h1>

            <div class="subtitle">
                ${data.stats.services} services •
                ${data.stats.domains} domains •
                ${data.stats.enabled} blocked
            </div>

        </div>

        <div class="toolbar">

            <input
                id="search"
                class="search"
                placeholder="Search services..."
                oninput="draw()">

            <button
                class="update-btn"
                onclick="updateCatalog()">

                Update Catalog

            </button>

        </div>

        <div
            id="categories"
            class="categories">
        </div>

        <div
            id="grid"
            class="grid">
        </div>
    `;
}

function buildCategories(){

    const categories =
        [...new Set(
            services.map(
                x => x.category
            )
        )].sort();

    const div =
        document.getElementById(
            "categories"
        );

    div.innerHTML = `
        <button
            class="category-btn active"
            onclick="selectCategory('all', this)">
            All
        </button>
    `;

    categories.forEach(cat => {

        const btn =
            document.createElement(
                "button"
            );

        btn.className =
            "category-btn";

        btn.innerText =
            categoryLabel(cat);

        btn.onclick =
            () => selectCategory(
                cat,
                btn
            );

        div.appendChild(btn);
    });
}

function selectCategory(
    category,
    button
){

    currentCategory =
        category;

    document
        .querySelectorAll(
            ".category-btn"
        )
        .forEach(
            x => x.classList.remove(
                "active"
            )
        );

    button.classList.add(
        "active"
    );

    draw();
}

async function toggleService(
    id,
    checkbox
){

    checkbox.disabled = true;

    try{

        const response =
            await fetch(
                '/api/toggle/' + id,
                {
                    method:'POST'
                }
            );

        const result =
            await response.json();

        if(!result.success){

            checkbox.checked =
                !checkbox.checked;

            alert(
                result.error ||
                'Toggle failed'
            );

            return;
        }

        const svc =
            services.find(
                x => x.id === id
            );

        if(svc){

            svc.enabled =
                result.enabled
                    ? 1
                    : 0;
        }

    }
    catch(ex){

        checkbox.checked =
            !checkbox.checked;

        alert(
            'Connection error'
        );
    }
    finally{

        checkbox.disabled = false;
    }
}

function addCategoryHeader(
    grid,
    category
){

    const section =
        document.createElement(
            "div"
        );

    section.className =
        "category-section";

    section.innerHTML = `
        <div class="category-separator">

            <div class="category-line"></div>

            <div class="category-title">
                ${categoryLabel(category)}
            </div>

            <div class="category-line"></div>

        </div>
    `;

    grid.appendChild(section);
}

function draw(){

    const search =
        (
            document.getElementById(
                'search'
            )?.value || ''
        )
        .toLowerCase();

    const grid =
        document.getElementById(
            'grid'
        );

    if(!grid)
        return;

    grid.innerHTML = '';

    const filtered =
        services.filter(service => {

            if(
                currentCategory !== 'all' &&
                service.category !== currentCategory
            ){
                return false;
            }

            return service.name
                .toLowerCase()
                .includes(search);
        });

    let lastCategory = null;

    filtered.forEach(service => {

        if(service.category !== lastCategory){

            addCategoryHeader(
                grid,
                service.category
            );

            lastCategory =
                service.category;
        }

        const card =
            document.createElement(
                'div'
            );

        card.className =
            'card';

        card.innerHTML = `
            <div class="row">

                <div class="left">

                    <div class="info">

                        <div class="title">
                            ${service.name}
                        </div>

                        <div class="meta">
                            ${categoryLabel(service.category)}
                            •
                            ${service.domain_count}
                            domains
                        </div>

                    </div>

                </div>

                <label class="switch">

                    <input
                        type="checkbox"
                        ${service.enabled ? 'checked' : ''}>

                    <span
                        class="slider">
                    </span>

                </label>

            </div>
        `;

        const checkbox =
            card.querySelector(
                'input'
            );

        checkbox.addEventListener(
            'change',
            () =>
                toggleService(
                    service.id,
                    checkbox
                )
        );

        grid.appendChild(
            card
        );
    });
}

function showToast(message, success = true){

    let toast =
        document.getElementById(
            "toast"
        );

    if(!toast){

        toast =
            document.createElement(
                "div"
            );

        toast.id = "toast";

        document.body.appendChild(
            toast
        );
    }

    toast.className =
        success
            ? "toast success show"
            : "toast error show";

    toast.textContent =
        message;

    clearTimeout(
        window.toastTimer
    );

    window.toastTimer =
        setTimeout(() => {

            toast.classList.remove(
                "show"
            );

        }, 3000);
}

async function updateCatalog(){

    const btn =
        document.querySelector(
            ".update-btn"
        );

    const oldText =
        btn.innerText;

    btn.disabled = true;
    btn.innerText =
        "Updating...";

    try{

        const response =
            await fetch(
                "/api/catalog/update",
                {
                    method: "POST"
                }
            );

        const result =
            await response.json();

        if(!result.success){

            throw new Error(
                result.error ||
                "Catalog update failed"
            );
        }

        showToast(
            result.message,
            true
        );

        await load();
    }
    catch(ex){

        showToast(
            ex.message,
            false
        );
    }
    finally{

        btn.disabled = false;
        btn.innerText =
            oldText;
    }
}

load();
