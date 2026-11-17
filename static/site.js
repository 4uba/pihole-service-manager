let services = [];
let currentCategory = "all";

async function load() {
    const response = await fetch("/api/services");
    const data = await response.json();

    services = data.services;

    renderPage(data);
    buildCategories();
    draw();
}

function renderPage(data) {

    document.getElementById("app").innerHTML = `
        <h1>Blocked Services</h1>

        <div class="subtitle">
            Allows to quickly block popular sites and services.
            (${data.stats.services} services,
             ${data.stats.domains} domains,
             ${data.stats.enabled} blocked)
        </div>

        <input
            id="search"
            class="search"
            placeholder="Search service..."
            oninput="draw()"
        >

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

function buildCategories() {

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
            onclick="selectCategory('all', this)"
        >
            All
        </button>
    `;

    categories.forEach(category => {

        const button =
            document.createElement(
                "button"
            );

        button.className =
            "category-btn";

        button.innerText =
            category;

        button.onclick =
            () => selectCategory(
                category,
                button
            );

        div.appendChild(button);

    });
}

function selectCategory(
    category,
    button
) {

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
) {

    checkbox.disabled = true;

    try {

        const response =
            await fetch(
                "/api/toggle/" + id,
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        if (!data.success) {

            checkbox.checked =
                !checkbox.checked;

            alert(
                data.error ||
                "Toggle failed"
            );

            return;
        }

        const svc =
            services.find(
                x => x.id === id
            );

        if (svc) {
            svc.enabled =
                data.enabled ? 1 : 0;
        }

    } catch (err) {

        checkbox.checked =
            !checkbox.checked;

        alert(
            "Connection error"
        );

    } finally {

        checkbox.disabled = false;
    }
}

function getIcon(service) {

    const name =
        service.name.toLowerCase();

    if (name.includes("chatgpt"))
        return "🤖";

    if (name.includes("discord"))
        return "🎮";

    if (name.includes("telegram"))
        return "✈️";

    if (name.includes("youtube"))
        return "▶️";

    if (name.includes("facebook"))
        return "📘";

    if (name.includes("netflix"))
        return "N";

    if (name.includes("steam"))
        return "🎮";

    return service.name
        .charAt(0)
        .toUpperCase();
}

function draw() {

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

    if (!grid)
        return;

    grid.innerHTML = "";

    services
        .filter(service => {

            if (
                currentCategory !== "all" &&
                service.category !== currentCategory
            ) {
                return false;
            }

            return service.name
                .toLowerCase()
                .includes(search);

        })
        .forEach(service => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "card";

            card.innerHTML = `
                <div class="row">

                    <div class="left">

                        <div class="icon">
                            ${getIcon(service)}
                        </div>

                        <div>

                            <div class="title">
                                ${service.name}
                            </div>

                            <div class="meta">
                                ${service.category}
                                •
                                ${service.domain_count}
                                domains
                            </div>

                        </div>

                    </div>

                    <label class="switch">

                        <input
                            type="checkbox"
                            ${service.enabled ? "checked" : ""}
                        >

                        <span
                            class="slider"
                        ></span>

                    </label>

                </div>
            `;

            const checkbox =
                card.querySelector(
                    "input"
                );

            checkbox.addEventListener(
                "change",
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

load();
