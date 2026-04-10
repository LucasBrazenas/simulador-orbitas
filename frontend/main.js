import * as THREE from "https://esm.sh/three@0.160.0";
import { OrbitControls } from "https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js";

const DISTANCE_SCALE = 1e9;
const VISIBLE_RADIUS_MULTIPLIER = 40;
const MIN_VISIBLE_RADIUS = 1.4;
const TRAIL_MAX_POINTS = 1500;
const STATUS_TIME_FORMATTER = new Intl.DateTimeFormat("es-AR", {
	dateStyle: "medium",
	timeStyle: "medium",
});

const BASE_BODY_CONFIGS = [
	{
		name: "Sol",
		label: "Sol",
		color: 0xffe08a,
		radiusMeters: 695_700_000,
		rotationSpeed: 0.0015,
		texturePath: "./textures/sun.jpg",
	},
	{
		name: "Mercurio",
		label: "Mercurio",
		color: 0xb2a394,
		radiusMeters: 2_439_700,
		rotationSpeed: 0.003,
		texturePath: "./textures/Mercury.jpg",
		trailColor: 0xc6b7a8,
	},
	{
		name: "Venus",
		label: "Venus",
		color: 0xd9b36d,
		radiusMeters: 6_051_800,
		rotationSpeed: 0.002,
		texturePath: "./textures/Venus.jpg",
		trailColor: 0xe2bf82,
	},
	{
		name: "Tierra",
		label: "Tierra",
		color: 0x7bb0ff,
		radiusMeters: 6_371_000,
		rotationSpeed: 0.01,
		texturePath: "./textures/earth.jpg",
		trailColor: 0x76b6ff,
	},
	{
		name: "Luna",
		label: "Luna",
		color: 0xd0d0d0,
		radiusMeters: 1_737_400,
		rotationSpeed: 0.006,
		texturePath: "./textures/moon.jpg",
	},
	{
		name: "Marte",
		label: "Marte",
		color: 0xc96b3b,
		radiusMeters: 3_389_500,
		rotationSpeed: 0.009,
		texturePath: "./textures/Mars.jpg",
		trailColor: 0xda7d56,
	},
	{
		name: "Jupiter",
		label: "Júpiter",
		color: 0xdab07c,
		radiusMeters: 69_911_000,
		rotationSpeed: 0.02,
		texturePath: "./textures/Jupiter.jpg",
		trailColor: 0xd7b088,
	},
	{
		name: "Saturno",
		label: "Saturno",
		color: 0xd8c18d,
		radiusMeters: 58_232_000,
		rotationSpeed: 0.018,
		texturePath: "./textures/Saturn.jpg",
		trailColor: 0xdcc998,
	},
	{
		name: "Urano",
		label: "Urano",
		color: 0x95daef,
		radiusMeters: 25_362_000,
		rotationSpeed: 0.014,
		texturePath: "./textures/Uranus.jpg",
		trailColor: 0x9de5f2,
	},
	{
		name: "Neptuno",
		label: "Neptuno",
		color: 0x5375ff,
		radiusMeters: 24_622_000,
		rotationSpeed: 0.014,
		texturePath: "./textures/Neptune.jpg",
		trailColor: 0x6d86f3,
	},
];

const BASE_BODY_CONFIG_BY_NAME = Object.fromEntries(
	BASE_BODY_CONFIGS.map((config) => [config.name, config]),
);
const customBodyConfigs = {};

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x02050b);

const camera = new THREE.PerspectiveCamera(
	60,
	window.innerWidth / window.innerHeight,
	0.1,
	20_000,
);
camera.position.set(0, 900, 5500);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 8;
controls.maxDistance = 14_000;
controls.maxPolarAngle = Math.PI;

const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
scene.add(ambientLight);

const pointLight = new THREE.PointLight(0xffffff, 3.5);
scene.add(pointLight);

const axesHelper = new THREE.AxesHelper(220);
scene.add(axesHelper);

const gridHelper = new THREE.GridHelper(10_000, 40, 0x283244, 0x111826);
gridHelper.rotation.x = Math.PI / 2;
scene.add(gridHelper);

const textureLoader = new THREE.TextureLoader();
const textures = Object.fromEntries(
	BASE_BODY_CONFIGS.filter((config) => config.texturePath).map((config) => [
		config.name,
		{ map: textureLoader.load(config.texturePath) },
	]),
);

const bodies = {};
const trails = {};
const trailPoints = {};
const followOptions = {};

let followTargetName = "";
let sizeMode = "visible";

const followTargetSelect = document.getElementById("follow-target");
const sizeModeSelect = document.getElementById("size-mode");
const timeScaleInput = document.getElementById("time-scale-input");
const timeScaleLabel = document.getElementById("time-scale-label");
const simulationTimeLabel = document.getElementById("simulation-time-label");
const syncNowButton = document.getElementById("sync-now-button");
const customNameInput = document.getElementById("custom-name");
const customMassInput = document.getElementById("custom-mass");
const customRadiusInput = document.getElementById("custom-radius");
const customColorInput = document.getElementById("custom-color");
const customPosXInput = document.getElementById("custom-pos-x");
const customPosYInput = document.getElementById("custom-pos-y");
const customPosZInput = document.getElementById("custom-pos-z");
const customVelXInput = document.getElementById("custom-vel-x");
const customVelYInput = document.getElementById("custom-vel-y");
const customVelZInput = document.getElementById("custom-vel-z");
const addCustomBodyButton = document.getElementById("add-custom-body-button");
const resetSystemButton = document.getElementById("reset-system-button");
const customBodyStatus = document.getElementById("custom-body-status");
const customBodyList = document.getElementById("custom-body-list");

function getAllBodyConfigs() {
	return [...BASE_BODY_CONFIGS, ...Object.values(customBodyConfigs)];
}

function getBodyConfig(name) {
	return customBodyConfigs[name] || BASE_BODY_CONFIG_BY_NAME[name] || null;
}

function parseColorToHex(color) {
	try {
		return new THREE.Color(color).getHex();
	} catch {
		return 0xff6b4a;
	}
}

function setCustomBodyStatus(message = "", tone = "") {
	customBodyStatus.textContent = message;
	customBodyStatus.className = "form-status";

	if (tone) {
		customBodyStatus.classList.add(tone);
	}
}

function registerFollowOption(name, label) {
	if (followOptions[name]) return;

	const option = document.createElement("option");
	option.value = name;
	option.textContent = label;
	followTargetSelect.appendChild(option);
	followOptions[name] = option;
}

function unregisterFollowOption(name) {
	const option = followOptions[name];
	if (!option) return;

	option.remove();
	delete followOptions[name];
}

function updateExistingBodyVisuals(config) {
	const mesh = bodies[config.name];
	if (!mesh) return;

	mesh.material.color.setHex(config.color);
}

function getVisualRadius(config) {
	const realRadiusUnits = config.radiusMeters / DISTANCE_SCALE;

	if (sizeMode === "real") {
		return realRadiusUnits;
	}

	return Math.max(
		Math.sqrt(realRadiusUnits) * VISIBLE_RADIUS_MULTIPLIER,
		MIN_VISIBLE_RADIUS,
	);
}

function getFollowOffset(config) {
	const visualRadius = getVisualRadius(config);
	const distance = Math.max(visualRadius * 10, 14);
	return new THREE.Vector3(distance * 0.35, distance * 0.25, distance);
}

function getBodyPosition(positionMeters) {
	return new THREE.Vector3(
		positionMeters[0] / DISTANCE_SCALE,
		positionMeters[1] / DISTANCE_SCALE,
		positionMeters[2] / DISTANCE_SCALE,
	);
}

function getMoonVisiblePosition(moonPositionMeters, earthPositionMeters) {
	const moonPosition = getBodyPosition(moonPositionMeters);
	const earthPosition = getBodyPosition(earthPositionMeters);

	if (sizeMode === "real") {
		return moonPosition;
	}

	const earthConfig = getBodyConfig("Tierra");
	const moonConfig = getBodyConfig("Luna");
	const relative = moonPosition.clone().sub(earthPosition);
	const minimumVisibleSeparation =
		getVisualRadius(earthConfig) + getVisualRadius(moonConfig) + 0.8;

	if (relative.length() === 0) {
		relative.set(minimumVisibleSeparation, 0, 0);
	} else if (relative.length() < minimumVisibleSeparation) {
		relative.setLength(minimumVisibleSeparation);
	}

	return earthPosition.add(relative);
}

function applyBodyScales() {
	getAllBodyConfigs().forEach((config) => {
		const mesh = bodies[config.name];
		if (!mesh) return;

		mesh.scale.setScalar(getVisualRadius(config));
	});
}

function createTrail(config) {
	if (!config.trailColor || trails[config.name]) return;

	const geometry = new THREE.BufferGeometry();
	const material = new THREE.LineBasicMaterial({
		color: config.trailColor,
		transparent: true,
		opacity: 0.7,
	});
	const line = new THREE.Line(geometry, material);
	scene.add(line);

	trails[config.name] = { geometry, line };
	trailPoints[config.name] = [];
}

function updateTrail(bodyName, position) {
	const trail = trails[bodyName];
	const points = trailPoints[bodyName];

	if (!trail || !points) return;

	points.push(position.clone());

	if (points.length > TRAIL_MAX_POINTS) {
		points.shift();
	}

	trail.geometry.setFromPoints(points);
}

function clearAllTrails() {
	Object.keys(trailPoints).forEach((bodyName) => {
		trailPoints[bodyName] = [];

		const trail = trails[bodyName];
		if (trail) {
			trail.geometry.setFromPoints([]);
		}
	});
}

function createBody(config) {
	if (bodies[config.name]) return;

	const geometry = new THREE.SphereGeometry(1, 64, 64);
	const textureMap = config.texturePath ? textures[config.name]?.map || null : null;
	const material =
		config.name === "Sol"
			? new THREE.MeshBasicMaterial({
					color: config.color,
					map: textureMap,
				})
			: new THREE.MeshStandardMaterial({
					color: config.color,
					map: textureMap,
					metalness: 0.08,
					roughness: 0.85,
				});

	const mesh = new THREE.Mesh(geometry, material);
	mesh.position.set(0, 0, 0);

	scene.add(mesh);
	bodies[config.name] = mesh;
	createTrail(config);
}

function removeBody(name) {
	const mesh = bodies[name];
	if (mesh) {
		scene.remove(mesh);
		mesh.geometry.dispose();
		mesh.material.dispose();
		delete bodies[name];
	}

	const trail = trails[name];
	if (trail) {
		scene.remove(trail.line);
		trail.geometry.dispose();
		trail.line.material.dispose();
		delete trails[name];
		delete trailPoints[name];
	}

	if (customBodyConfigs[name]) {
		delete customBodyConfigs[name];
	}

	unregisterFollowOption(name);

	if (followTargetName === name) {
		followTargetName = "";
		followTargetSelect.value = "";
	}
}

function upsertBodyConfigFromSnapshot(bodyInfo) {
	const colorHex = parseColorToHex(bodyInfo.color || "#ff6b4a");
	const radiusMeters = Number(bodyInfo.radiusMeters) || 10_000_000;
	const existingConfig = getBodyConfig(bodyInfo.name);

	if (existingConfig) {
		existingConfig.radiusMeters = radiusMeters;
		existingConfig.color = colorHex;
		updateExistingBodyVisuals(existingConfig);
		registerFollowOption(bodyInfo.name, existingConfig.label || bodyInfo.name);
		createBody(existingConfig);
		return;
	}

	if (bodyInfo.isCustom) {
		customBodyConfigs[bodyInfo.name] = {
			name: bodyInfo.name,
			label: bodyInfo.name,
			color: colorHex,
			radiusMeters,
			rotationSpeed: 0.008,
			texturePath: null,
			trailColor: colorHex,
		};

		registerFollowOption(bodyInfo.name, bodyInfo.name);
		createBody(customBodyConfigs[bodyInfo.name]);
		return;
	}

	const baseConfig = BASE_BODY_CONFIG_BY_NAME[bodyInfo.name];
	if (baseConfig) {
		baseConfig.radiusMeters = radiusMeters;
		baseConfig.color = colorHex;
		registerFollowOption(bodyInfo.name, baseConfig.label);
		createBody(baseConfig);
		updateExistingBodyVisuals(baseConfig);
	}
}

function syncBodiesFromSnapshot(snapshotBodies) {
	const snapshotNames = new Set(snapshotBodies.map((body) => body.name));

	snapshotBodies.forEach((body) => {
		upsertBodyConfigFromSnapshot(body);
	});

	Object.keys(bodies).forEach((name) => {
		if (!snapshotNames.has(name)) {
			removeBody(name);
		}
	});

	applyBodyScales();
}

function updateCustomBodyList(snapshotBodies) {
	const customBodies = snapshotBodies.filter((body) => body.isCustom);

	if (customBodies.length === 0) {
		customBodyList.textContent = "No hay cuerpos personalizados activos.";
		return;
	}

	customBodyList.textContent = `Cuerpos activos: ${customBodies
		.map((body) => body.name)
		.join(", ")}`;
}

function formatTimeScale(timeScale) {
	if (timeScale === 0) {
		return "Tiempo pausado";
	}

	if (timeScale === 1) {
		return "Tiempo real (1x)";
	}

	if (timeScale < 60) {
		return `${timeScale.toLocaleString("es-AR")}x tiempo real`;
	}

	if (timeScale < 3600) {
		return `1 s real = ${(timeScale / 60).toLocaleString("es-AR")} min simulados`;
	}

	if (timeScale < 86_400) {
		return `1 s real = ${(timeScale / 3600).toLocaleString("es-AR")} h simuladas`;
	}

	if (timeScale < 604_800) {
		return `1 s real = ${(timeScale / 86_400).toLocaleString("es-AR")} día(s) simulados`;
	}

	return `1 s real = ${(timeScale / 604_800).toLocaleString("es-AR")} semana(s) simuladas`;
}

function updateStatus(snapshot) {
	timeScaleLabel.textContent = formatTimeScale(snapshot.timeScale);
	simulationTimeLabel.textContent = `Tiempo simulado: ${STATUS_TIME_FORMATTER.format(
		new Date(snapshot.simulationTime),
	)}`;

	if (document.activeElement !== timeScaleInput) {
		timeScaleInput.value = String(Math.round(snapshot.timeScale));
	}
}

function sendSocketMessage(message) {
	if (socket.readyState !== WebSocket.OPEN) return;
	socket.send(JSON.stringify(message));
}

function commitTimeScale(value) {
	const parsedValue = Number(value);
	if (!Number.isFinite(parsedValue) || parsedValue < 0) return;

	timeScaleInput.value = String(parsedValue);
	sendSocketMessage({ type: "set_time_scale", value: parsedValue });
}

function buildCustomBodyPayload() {
	const name = customNameInput.value.trim();
	const mass = Number(customMassInput.value);
	const radiusMeters = Number(customRadiusInput.value);
	const positionAu = [
		Number(customPosXInput.value),
		Number(customPosYInput.value),
		Number(customPosZInput.value),
	];
	const velocityKmS = [
		Number(customVelXInput.value),
		Number(customVelYInput.value),
		Number(customVelZInput.value),
	];

	if (!name) {
		throw new Error("El nombre no puede estar vacío.");
	}

	if (getBodyConfig(name)) {
		throw new Error("Ya existe un cuerpo con ese nombre.");
	}

	if (!Number.isFinite(mass) || mass <= 0) {
		throw new Error("La masa debe ser un número positivo.");
	}

	if (!Number.isFinite(radiusMeters) || radiusMeters <= 0) {
		throw new Error("El radio debe ser un número positivo.");
	}

	if (
		[...positionAu, ...velocityKmS].some(
			(component) => !Number.isFinite(component),
		)
	) {
		throw new Error("Posición y velocidad deben tener números válidos.");
	}

	return {
		type: "add_custom_body",
		name,
		mass,
		radiusMeters,
		color: customColorInput.value,
		positionAu,
		velocityKmS,
	};
}

BASE_BODY_CONFIGS.forEach((config) => {
	registerFollowOption(config.name, config.label);
	createBody(config);
});
applyBodyScales();

followTargetSelect.addEventListener("change", (event) => {
	followTargetName = event.target.value;
});

sizeModeSelect.addEventListener("change", (event) => {
	sizeMode = event.target.value;
	applyBodyScales();
});

timeScaleInput.addEventListener("change", () => {
	commitTimeScale(timeScaleInput.value);
});

timeScaleInput.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		commitTimeScale(timeScaleInput.value);
	}
});

document.querySelectorAll(".preset-scale").forEach((button) => {
	button.addEventListener("click", () => {
		commitTimeScale(button.dataset.scale);
	});
});

syncNowButton.addEventListener("click", () => {
	clearAllTrails();
	sendSocketMessage({ type: "sync_to_now" });
	setCustomBodyStatus("Sistema resincronizado al instante actual.", "success");
});

addCustomBodyButton.addEventListener("click", () => {
	try {
		const payload = buildCustomBodyPayload();
		sendSocketMessage(payload);
		setCustomBodyStatus("Cuerpo enviado al backend.", "success");
	} catch (error) {
		setCustomBodyStatus(error.message, "error");
	}
});

resetSystemButton.addEventListener("click", () => {
	clearAllTrails();
	sendSocketMessage({ type: "reset_system" });
	setCustomBodyStatus("Sistema reiniciado sin cuerpos extra.", "success");
});

const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
	console.log("WebSocket conectado");
	commitTimeScale(timeScaleInput.value);
};

socket.onmessage = (event) => {
	const message = JSON.parse(event.data);
	if (message.type !== "snapshot") return;

	syncBodiesFromSnapshot(message.bodies);
	updateCustomBodyList(message.bodies);
	updateStatus(message);

	const positionsByName = Object.fromEntries(
		message.bodies.map((body) => [body.name, body.position]),
	);

	message.bodies.forEach((body) => {
		const mesh = bodies[body.name];
		if (!mesh) return;

		if (body.name === "Luna" && positionsByName.Tierra) {
			mesh.position.copy(
				getMoonVisiblePosition(body.position, positionsByName.Tierra),
			);
		} else {
			mesh.position.copy(getBodyPosition(body.position));
		}

		if (trails[body.name]) {
			updateTrail(body.name, mesh.position);
		}
	});
};

socket.onerror = (error) => {
	console.error("Error WebSocket:", error);
	timeScaleLabel.textContent = "Sin conexión con el backend";
};

socket.onclose = () => {
	console.warn("WebSocket cerrado");
	timeScaleLabel.textContent = "Conexión cerrada";
};

window.addEventListener("resize", () => {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
	requestAnimationFrame(animate);

	getAllBodyConfigs().forEach((config) => {
		const mesh = bodies[config.name];
		if (!mesh) return;

		mesh.rotation.y += config.rotationSpeed;
	});

	if (followTargetName) {
		const targetMesh = bodies[followTargetName];
		const targetConfig = getBodyConfig(followTargetName);

		if (targetMesh && targetConfig) {
			const desiredPosition = targetMesh.position
				.clone()
				.add(getFollowOffset(targetConfig));
			camera.position.lerp(desiredPosition, 0.08);
			controls.target.lerp(targetMesh.position, 0.08);
		}
	}

	controls.update();
	renderer.render(scene, camera);
}

animate();
