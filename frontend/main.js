import * as THREE from "https://esm.sh/three@0.160.0";
import { OrbitControls } from "https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);

const camera = new THREE.PerspectiveCamera(
	60,
	window.innerWidth / window.innerHeight,
	0.1,
	5000,
);

camera.position.set(0, 0, 260);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 50;
controls.maxDistance = 2000;
controls.maxPolarAngle = Math.PI / 2;

// =========================
// LUCES
// =========================
const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
scene.add(ambientLight);

const pointLight = new THREE.PointLight(0xffffff, 3);
pointLight.position.set(0, 0, 0);
scene.add(pointLight);

// =========================
// AYUDAS VISUALES
// =========================
const axesHelper = new THREE.AxesHelper(50);
scene.add(axesHelper);

const gridHelper = new THREE.GridHelper(400, 20, 0x444444, 0x222222);
scene.add(gridHelper);

// =========================
// TEXTURAS
// =========================
const textureLoader = new THREE.TextureLoader();

const textures = {
	Sol: {
		map: textureLoader.load("./textures/sun.jpg"),
	},
	Tierra: {
		map: textureLoader.load("./textures/earth.jpg"),

		// opcionales, si después conseguís estas imágenes:
		// bumpMap: textureLoader.load("./textures/earth_bump.jpg"),
		// normalMap: textureLoader.load("./textures/earth_normal.jpg"),
		// roughnessMap: textureLoader.load("./textures/earth_roughness.jpg"),
	},
	Luna: {
		map: textureLoader.load("./textures/moon.jpg"),
	},
};

// =========================
// CUERPOS
// =========================
const bodies = {};

let followTarget = null;
let followOffset = new THREE.Vector3(0, 20, 40);

function setCameraTarget(bodyName) {
	if (!bodyName) {
		followTarget = null;
		return;
	}

	const targetMesh = bodies[bodyName];
	if (!targetMesh) return;

	followTarget = targetMesh;
}

window.addEventListener("keydown", (event) => {
	switch (event.key) {
		case "0":
			setCameraTarget(null);
			console.log("Cámara libre");
			break;
		case "1":
			setCameraTarget("Sol");
			console.log("Siguiendo al Sol");
			break;
		case "2":
			setCameraTarget("Tierra");
			console.log("Siguiendo a la Tierra");
			break;
		case "3":
			setCameraTarget("Luna");
			console.log("Siguiendo a la Luna");
			break;
	}
});

function createBody(name, color, size) {
	const geometry = new THREE.SphereGeometry(size, 64, 64);

	const bodyTextures = textures[name];

	let material;

	if (name === "Sol") {
		material = new THREE.MeshBasicMaterial({
			color,
			map: bodyTextures?.map || null,
		});
	} else {
		material = new THREE.MeshStandardMaterial({
			color,
			map: bodyTextures?.map || null,
			// bumpMap: bodyTextures?.bumpMap || null,
			// bumpScale: 0.2,
			// normalMap: bodyTextures?.normalMap || null,
			metalness: 0.1,
			roughness: 0.8,
		});
	}

	const mesh = new THREE.Mesh(geometry, material);
	scene.add(mesh);

	bodies[name] = mesh;
	return mesh;
}

createBody("Sol", 0xffff00, 12);
createBody("Tierra", 0xffffff, 4);
createBody("Luna", 0xaaaaaa, 1.5);

// =========================
// ESCALA VISUAL
// =========================
const SCALE = 1e9;

// posición inicial
bodies["Sol"].position.set(0, 0, 0);
bodies["Tierra"].position.set(149.6, 0, 0);
bodies["Luna"].position.set(149.6 + 0.384, 0, 0);

// =========================
// ESTELA DE LA TIERRA
// =========================
const trailPoints = [];
const trailMaterial = new THREE.LineBasicMaterial({ color: 0x66aaff });
const trailGeometry = new THREE.BufferGeometry();
const trailLine = new THREE.Line(trailGeometry, trailMaterial);
scene.add(trailLine);

function updateTrail(position) {
	trailPoints.push(position.clone());

	if (trailPoints.length > 1000) {
		trailPoints.shift();
	}

	trailGeometry.setFromPoints(trailPoints);
}

// =========================
// WEBSOCKET
// =========================
const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
	console.log("WebSocket conectado");
};

socket.onmessage = (event) => {
	const data = JSON.parse(event.data);

	let tierraData = null;
	let lunaData = null;

	data.forEach((body) => {
		if (body.name === "Tierra") tierraData = body;
		if (body.name === "Luna") lunaData = body;
	});

	data.forEach((body) => {
		const mesh = bodies[body.name];
		if (!mesh) return;

		// Sol y Tierra: escala normal
		if (body.name !== "Luna") {
			const x = body.position[0] / SCALE;
			const y = body.position[1] / SCALE;
			const z = body.position[2] / SCALE;

			mesh.position.set(x, y, z);

			if (body.name === "Tierra") {
				updateTrail(mesh.position);
			}
			return;
		}

		// Luna: exageramos la distancia respecto a la Tierra
		if (body.name === "Luna" && tierraData) {
			const tierraPos = new THREE.Vector3(
				tierraData.position[0] / SCALE,
				tierraData.position[1] / SCALE,
				tierraData.position[2] / SCALE,
			);

			const lunaRealPos = new THREE.Vector3(
				body.position[0] / SCALE,
				body.position[1] / SCALE,
				body.position[2] / SCALE,
			);

			const relative = lunaRealPos.clone().sub(tierraPos);

			// exagerar separación visual Luna-Tierra
			const moonDistanceBoost = 30;

			mesh.position.copy(
				tierraPos.clone().add(relative.multiplyScalar(moonDistanceBoost)),
			);
		}
	});
};

socket.onerror = (err) => {
	console.error("Error WebSocket:", err);
};

socket.onclose = () => {
	console.warn("WebSocket cerrado");
};

// =========================
// RESIZE
// =========================
window.addEventListener("resize", () => {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(window.innerWidth, window.innerHeight);
});

// =========================
// ANIMACIÓN
// =========================
function animate() {
	requestAnimationFrame(animate);

	if (bodies["Sol"]) bodies["Sol"].rotation.y += 0.002;
	if (bodies["Tierra"]) bodies["Tierra"].rotation.y += 0.01;
	if (bodies["Luna"]) bodies["Luna"].rotation.y += 0.008;

	if (followTarget) {
		const desiredPosition = followTarget.position.clone().add(followOffset);
		camera.position.lerp(desiredPosition, 0.08);
		controls.target.lerp(followTarget.position, 0.08);
	}

	controls.update();
	renderer.render(scene, camera);
}

animate();
