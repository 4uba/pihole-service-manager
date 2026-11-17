let services = [];
let currentCategory = "all";

async function load(){

    const r =
        await fetch("/api/services");

    const data =
        await r.json();

    services =
        data.services;

    document.getElementById(
        "app"
    ).innerHTML =
        render(data);

    buildCategories();

    draw();
}

function render(data){

    return `
    <div class="header">

        <h1>Service Manager V3</h1>

        <div class="stats">

            <div class="stat">
                <div class="stat-value">
                    ${data.stats.services}
                </div>
                <div class="stat-label">
                    Services
                </div>
            </div>

            <div class="stat">
                <div class="stat-value">
                    ${data.stats.domains}
                </div>
                <div class="stat-label">
                    Domains
                </div>
            </div>

            <div class="stat">
                <div class="stat-value">
                    ${data.stats.enabled}
                </div>
                <div class="stat-label">
                    Blocked
                </div>
            </div>

        </div>

    </div>

    <div class="toolbar">

        <input
            id="search"
            class="search"
            placeholder="Search service..."
            oninput="draw()"
        >

    </div>

    <div
        id="categories"
        class="categories"
    ></div>

    <div
        id="grid"
        class="grid"
    ></div>
    `;
}

function buildCategories(){

    const categories =
        [...new Set(
            services.map(
                x => x.category
            )
        )]
        .sort();

    const div =
        document.getElementById(
            "categories"
        );

    div.innerHTML =
        `
        <button
            class="category-btn active"
            onclick="selectCategory('all',this)"
        >
            All
        </button>
        `;

    categories.forEach(cat => {

        const button =
            document.createElement(
                "button"
            );

        button.className =
            "category-btn";

        button.innerText =
            cat;

        button.onclick =
            () => selectCategory(
                cat,
                button
            );

        div.appendChild(button);

    });

}

function selectCategory(category,button){

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

async function toggleService(id){

    const r =
        await fetch(
            "/api/toggle/" + id,
            {
                method:"POST"
            }
        );

    const result =
        await r.json();

    if(!result.success){
        alert(
            result.error || "Toggle failed"
        );
        return;
    }

    const svc =
        services.find(
            x => x.id === id
        );

    if(svc)
        svc.enabled =
            result.enabled ? 1 : 0;

    draw();
}

function draw(){

    const search =
        (
            document.getElementById(
                "search"
            )?.value || ""
        )
        .toLowerCase();

    const grid =
        document.getElementById(
            "grid"
        );

    if(!grid)
        return;

    grid.innerHTML = "";

    services
        .filter(x => {

            if(
                currentCategory !== "all" &&
                x.category !== currentCategory
            ){
                return false;
            }

            return x.name
                .toLowerCase()
                .includes(search);

        })
        .forEach(x => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "card";

            if(x.enabled)
                card.classList.add(
                    "blocked"
                );

            const big =
                x.domain_count >= 100
                ? '<div class="big">HIGH IMPACT</div>'
                : '';

            const badgeClass = [
                "ai",
                "streaming",
                "gaming",
                "social_network",
                "shopping",
                "messenger"
            ].includes(
                x.category
            )
                ? x.category
                : "default";

            const actionText =
                x.enabled
                    ? "UNBLOCK"
                    : "BLOCK";

            card.innerHTML =
                `
                <div class="card-top">

                    <div class="badge ${badgeClass}">
                        ${x.category}
                    </div>

                </div>

                <div class="name">
                    ${x.name}
                </div>

                <div class="meta">
                    ${x.domain_count}
                    domains
                </div>

                ${big}

                <div class="status ${
                    x.enabled
                    ? "blocked"
                    : "allowed"
                }">

                    ${
                        x.enabled
                        ? "BLOCKED"
                        : "ALLOWED"
                    }

                </div>

                <button
                    class="toggle-btn"
                    onclick="toggleService('${x.id}')"
                >
                    ${actionText}
                </button>
                `;

            grid.appendChild(card);

        });

}

(async() => {

    await load();

})();
