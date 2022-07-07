package main


import (
	"dagger.io/dagger"
    "universe.dagger.io/alpha/kubernetes/kapp"
)

dagger.#Plan & {
	actions: test: {
		deploy: kapp.#Deploy & {
			app:        "demo-app"
			fs:         client.filesystem."./".read.contents
			kubeConfig: client.commands.kc.stdout
			file:       "./release/kubernetes-manifests.yaml"
		}
		ls: kapp.#List & {
			fs:         client.filesystem."./".read.contents
			kubeConfig: client.commands.kc.stdout
			namespace:  "default"
		}
		inspect: kapp.#Inspect & {
			app:        "demo-app"
			fs:         client.filesystem."./".read.contents
			kubeConfig: client.commands.kc.stdout
		}
		delete: kapp.#Delete & {
			app:        "demo-app"
			fs:         client.filesystem."./".read.contents
			kubeConfig: client.commands.kc.stdout
		}
	}

	client: {
		commands: kc: {
			name: "kubectl"
			args: ["config", "view", "--raw"]
			stdout: dagger.#Secret
		}
		filesystem: "./": read: {
			contents: dagger.#FS
			include: ["./release/kubernetes-manifests.yaml"]
		}
	}
}